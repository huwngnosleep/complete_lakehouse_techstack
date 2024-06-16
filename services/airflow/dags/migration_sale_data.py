import os
from datetime import datetime
from airflow import DAG
import pandas
import pymssql
from tempfile import NamedTemporaryFile
import pyhdfs
from pyhive import hive
import subprocess
from airflow.decorators import dag, task_group, task
from schema.sale_data_schema import ALL_TABLES
from pyhive.exc import Error
DAG_ID = "migration_sale_data"
DAG_SCHEDULE = "*/10 * * * *"
with DAG(
    DAG_ID,
    # schedule=DAG_SCHEDULE,
    catchup=False,
    # start_date=datetime(2024, 1, 1),
) as dag:
    ls_raw_tables = [
        "categories",
        "brands",
        "products",
        "customers",
        "stores",
        "staffs",
        "orders",
        "order_items",
        "stocks",
    ]
    BASE_PATH = '/sale_warehouse'
    RAW = "/raw"
    WAREHOUSE = "/warehouse"
    @task_group(group_id='get_raw_data')
    def get_raw_data():
        for table in ls_raw_tables:
            @dag.task(task_id=f"extract_raw_{table}")
            def extract_raw(table):
                hdfs_raw_dir = f"{BASE_PATH}{RAW}/{table}/"
                dest_file_name = f"{table}_01.snappy.parquet"
                mssql_conn = pymssql.connect('mssql:1433', 'sa', 'root@@@123', "BikeStores")
                hdfs_client = pyhdfs.HdfsClient(hosts='namenode:9870')
                raw_data = pandas.read_sql(f"SELECT * FROM {table};", mssql_conn)
                temp_file = NamedTemporaryFile()
                raw_data.to_parquet(temp_file.name)
                # clean_raw_dir = subprocess.run(f"/hadoop/bin/hdfs dfs -fs hdfs://namenode:9000 -rm -r -f {hdfs_raw_dir}"
                #                , shell=True
                #                , stdout=subprocess.PIPE
                #                , stderr=subprocess.PIPE)
                # print("clean_raw_dir OUTPUT:", clean_raw_dir.stdout)
                # print("clean_raw_dir ERROR:", clean_raw_dir.stderr)
                hdfs_client.delete(hdfs_raw_dir, recursive=True)
                if not hdfs_client.exists(hdfs_raw_dir):
                    hdfs_client.mkdirs(hdfs_raw_dir)
                hdfs_client.copy_from_local(
                    localsrc=temp_file.name, 
                    dest=hdfs_raw_dir + dest_file_name,
                    overwrite=True,
                    async_=True
                )
                # hdfs_client.create(
                #     data=temp_file.name, 
                #     path=hdfs_raw_dir + dest_file_name,
                #     overwrite=True,
                # )
                # upload_to_hdfs = subprocess.run(f"/hadoop/bin/hdfs dfs -fs hdfs://namenode:9000 -put -f {temp_file.name} {hdfs_raw_dir + dest_file_name}"
                #                , shell=True
                #                , stdout=subprocess.PIPE
                #                , stderr=subprocess.PIPE)
                # print("upload_to_hdfs OUTPUT:", upload_to_hdfs.stdout)
                # print("upload_to_hdfs ERROR:", upload_to_hdfs.stderr)
                mssql_conn.close()
            extract_raw(table)
    
    @task_group(group_id='load_staging')
    def load_staging():
        for table in ls_raw_tables:
            @dag.task(task_id=f"create_staging_{table}")
            def create_staging_table(table):
                connection = hive.connect(host='spark-thriftserver', port=10000)
                cursor = connection.cursor() 
                raw_table_name = f"default.{table}"
                cursor.execute(f"""
                    DROP TABLE IF EXISTS {raw_table_name}
                """)
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {raw_table_name}
                    USING parquet
                    LOCATION '{BASE_PATH}{RAW}/{table}/*.snappy.parquet'
                """)
            create_staging_table(table)
            
    @task_group(group_id='create_dwh_table')
    def create_datawarehouse_table():
        for table in ls_raw_tables:
            @dag.task(task_id=f"recreate_{table}")
            def recreate_warehouse_table(table):
                cursor = hive.connect(host='spark-thriftserver', port=10000).cursor() 
                cursor.execute(f"""
                    DROP TABLE IF EXISTS warehouse.{table}
                """)
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS warehouse.{table}
                    USING iceberg
                    LOCATION '{BASE_PATH}{WAREHOUSE}/{table}/*.snappy.parquet'
                """)
            recreate_warehouse_table(table)
         
    @task_group(group_id='insert_warehouse')        
    def insert_into_warehouse():
        for table in ls_raw_tables:
            @dag.task(task_id=f"insert_{table}")
            def insert_warehouse_table(table):
                raw_table_name = f"default.{table}"
                cursor = hive.connect(host='spark-thriftserver', port=10000).cursor() 
                cursor.execute(f"""
                    INSERT INTO warehouse.{table}
                    SELECT * FROM {raw_table_name}
                """)
            insert_warehouse_table(table)
            
    get_raw_data() >> load_staging() >> create_datawarehouse_table() >> insert_into_warehouse()