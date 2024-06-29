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
from schema.sale_aggregate_schema import SALE_AGGREGATE_TABLES
from pyhive.exc import Error
from clickhouse_driver import Client

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
                
                # extract raw data to parquet files
                extract_query = f"SELECT * FROM {table};"
                raw_data = pandas.read_sql(extract_query, mssql_conn)
                print(extract_query)
                temp_file = NamedTemporaryFile()
                raw_data.to_parquet(temp_file.name)
                
                # upload to HDFS
                hdfs_client.delete(hdfs_raw_dir, recursive=True)
                if not hdfs_client.exists(hdfs_raw_dir):
                    hdfs_client.mkdirs(hdfs_raw_dir)
                hdfs_client.copy_from_local(
                    localsrc=temp_file.name, 
                    dest=hdfs_raw_dir + dest_file_name,
                    overwrite=True,
                    async_=True
                )
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
                warehouse_table_name = f"iceberg.warehouse.{table}"
                cursor = hive.connect(host='spark-thriftserver', port=10000).cursor() 
                cursor.execute(f"""
                    DROP TABLE IF EXISTS {warehouse_table_name}
                """)
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {warehouse_table_name} (
                        {",".join(list(map(lambda col: f'{col["name"]} {col["type"]}', ALL_TABLES[table]["schema"])))}
                    )
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
                warehouse_table_name = f"iceberg.warehouse.{table}"
                cursor = hive.connect(host='spark-thriftserver', port=10000).cursor() 
                cursor.execute(f"""
                    INSERT INTO {warehouse_table_name}
                    SELECT * FROM {raw_table_name}
                """)
            insert_warehouse_table(table)
            
    @task_group(group_id='aggregate_warehouse')        
    def aggregate_warehouse():
        for table in SALE_AGGREGATE_TABLES:
            @dag.task(task_id=f"aggregate_{table}")
            def aggregate_into_warehouse():
                cursor = hive.connect(host='spark-thriftserver', port=10000).cursor() 
                cursor.execute(f"DROP TABLE IF EXISTS iceberg.aggr_warehouse.{table}")
                cursor.execute(SALE_AGGREGATE_TABLES[table]["create_table_command"])
                hdfs_client = pyhdfs.HdfsClient(hosts='namenode:9870')
                hdfs_client.delete(f"/user/hive/warehouse/aggr_warehouse.db/{table}_parquet", recursive=True)
                cursor.execute(f"""
                    DROP TABLE IF EXISTS spark_catalog.aggr_warehouse.{table}_parquet
                """)
                cursor.execute(f"""
                    CREATE TABLE spark_catalog.aggr_warehouse.{table}_parquet
                    USING parquet
                    AS
                    SELECT * FROM iceberg.aggr_warehouse.{table}
                """)
            aggregate_into_warehouse()
            
    @task_group(group_id='load_to_clickhouse')        
    def load_to_clickhouse():
        for table in SALE_AGGREGATE_TABLES:
            @dag.task(task_id=f"load_to_clickhouse_{table}")
            def load_to_clickhouse():
                clickhouse_client = Client('clickhouse1', database="default")
                clickhouse_client.execute(f"""
                    CREATE OR REPLACE TABLE {table}_hdfs
                    ENGINE=HDFS('hdfs://namenode:9000/user/hive/warehouse/aggr_warehouse.db/{table}_parquet/*.snappy.parquet', 'Parquet')                          
                """)
                clickhouse_client.execute(f"""
                    CREATE OR REPLACE TABLE {table} ON CLUSTER clickhouse_cluster
                    AS {table}_hdfs
                    ENGINE=MergeTree()
                    ORDER BY (date(order_date))    
                    SETTINGS allow_nullable_key=true                      
                """)
                clickhouse_client.execute(f"""
                    INSERT INTO {table} SELECT * FROM {table}_hdfs
                """)
            load_to_clickhouse()
            
    get_raw_data() >> load_staging() >> create_datawarehouse_table() >> insert_into_warehouse() >> aggregate_warehouse() >> load_to_clickhouse()