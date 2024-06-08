import os
from datetime import datetime
from airflow import DAG
import pandas
import pymssql
from tempfile import NamedTemporaryFile
import pyhdfs
DAG_ID = "migration_sale_data"
with DAG(
    DAG_ID,
    schedule=None,
    catchup=False,
) as dag:
    ls_raw_tables = [
        "production.categories",
        "production.brands",
        "production.products",
        "sales.customers",
        "sales.stores",
        "sales.staffs",
        "sales.orders",
        "sales.order_items",
        "production.stocks",
    ]
    
    @dag.task(task_id="get_raw_data")
    def get_raw_data():
        mssql_conn = pymssql.connect('mssql:1433', 'sa', 'root@@@123', "retail")
        hdfs_client = pyhdfs.HdfsClient(hosts='namenode:9870')
        for table in ls_raw_tables:
            raw_data = pandas.read_sql(f"SELECT * FROM {table};", mssql_conn)
            temp_file = NamedTemporaryFile()
            raw_data.to_parquet(temp_file.name)
            hdfs_raw_dir = f"/sale_warehouse/raw/{table}/"
            dest_file_name = f"{table}_01.snappy.parquet"
            hdfs_client.delete(hdfs_raw_dir + dest_file_name)
            if not hdfs_client.exists(hdfs_raw_dir):
                hdfs_client.mkdirs(hdfs_raw_dir)
            hdfs_client.copy_from_local(
                localsrc=temp_file.name, 
                dest=hdfs_raw_dir + dest_file_name
            )
        mssql_conn.close()
    get_raw_data()