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

def extract_raw(table, BASE_PATH, RAW, ext_from=None, ext_to=None):
    hdfs_raw_dir = f"{BASE_PATH}{RAW}/{table}/"
    dest_file_name = f"{table}_01.snappy.parquet"
    mssql_conn = pymssql.connect('mssql:1433', 'sa', 'root@@@123', "BikeStores")
    hdfs_client = pyhdfs.HdfsClient(hosts='namenode:9870')
    
    # extract raw data to parquet files
    extract_query = f"SELECT * FROM {table};"
    if ext_from and ext_to:
        extract_query = f"SELECT * FROM {table} WHERE updated_at BETWEEN '{ext_from}' and '{ext_to}';"
    
    raw_data = pandas.read_sql(extract_query, mssql_conn)
    print("NUM RECORD:", raw_data["updated_at"].count())
    raw_data = raw_data.drop('updated_at', axis=1)
    print("DEBUG:", extract_query)
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
    
    
def create_staging_table(table, BASE_PATH, RAW):
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
    
    
def recreate_warehouse_table(table, BASE_PATH, WAREHOUSE):
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
    
    
def insert_warehouse_table(table):
    raw_table_name = f"default.{table}"
    warehouse_table_name = f"iceberg.warehouse.{table}"
    cursor = hive.connect(host='spark-thriftserver', port=10000).cursor() 
    count_query = f"SELECT COUNT(*) FROM {raw_table_name}"
    cursor.execute(count_query)
    has_staging_data = cursor.fetchone()[0]
    print(count_query, "---", has_staging_data)
    if has_staging_data == 0:
        print("STAGING HAS NO DATA, SKIPPING...")
    else:
        # cursor.execute(f"""
        #     INSERT INTO {warehouse_table_name}
        #     SELECT * FROM {raw_table_name}
        # """)
        cursor.execute(f"""
            MERGE INTO {warehouse_table_name} t   
            USING {raw_table_name} s
            ON {' AND '.join(list(map(lambda col_name: f"t.{col_name}=s.{col_name}", ALL_TABLES[table]["primary_key"])))}
            WHEN MATCHED 
                THEN UPDATE SET 
                {','.join(list(map(lambda col: f"t.{col["name"]}=s.{col["name"]}", ALL_TABLES[table]["schema"])))}
            WHEN NOT MATCHED 
                THEN INSERT *
        """)
    
    
def aggregate_into_warehouse(table):
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
    

def load_to_clickhouse(table):
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