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
from airflow.operators.python_operator import PythonOperator
from airflow.utils.session import create_session
from airflow.models import DagRun
from airflow.models.taskinstance import TaskInstance
from airflow.utils.state import State


DAG_ID = "etl_classicmodels"
DAG_SCHEDULE = "* * * * *"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
with DAG(
    DAG_ID,
    schedule=DAG_SCHEDULE,
    catchup=False,
    max_active_runs=1,
    start_date=datetime(2024, 1, 1),
) as dag:
    ls_raw_tables = [
        "customers",
    ]
    BASE_PATH = '/sale_warehouse'
    RAW = "/raw"
    WAREHOUSE = "/warehouse"
    
    def create_staging_table(table, BASE_PATH, RAW):
        connection = hive.connect(host='spark-thriftserver', port=10000)
        cursor = connection.cursor() 
        cursor.execute("""
            DROP TABLE IF EXISTS spark_catalog.classicmodels.customers
        """)
        
        cursor.execute("""
            CREATE TABLE spark_catalog.classicmodels.customers
            USING parquet
            LOCATION '/classicmodels/raw/customers/*.snappy.parquet'
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS iceberg.classicmodels_warehouse.customers (
                timestamp TIMESTAMP,
                customerNumber String,
                customerName String,
                contactLastName String,
                contactFirstName String,
                phone String,
                addressLine1 String,
                addressLine2 String,
                city String,
                state String,
                postalCode String,
                country String,
                salesRepEmployeeNumber String,
                creditLimit String)
            USING iceberg
            LOCATION '/classicmodels/warehouse/customers/'
        """)
        
        cursor.execute("""
            MERGE INTO iceberg.classicmodels_warehouse.customers as target
            USING 
            (SELECT * FROM 
            (
                select 
                    timestamp,
                    cast(customerNumber as int) as customerNumber,
                    customerName,
                    contactLastName,
                    contactFirstName,
                    phone,
                    addressLine1,
                    addressLine2,
                    city,
                    state,
                    postalCode,
                    country,
                    salesRepEmployeeNumber,
                    creditLimit,
                    ROW_NUMBER() OVER (PARTITION BY customerNumber ORDER BY timestamp desc) as row_num
                from spark_catalog.classicmodels.customers
            ) where row_num = 1
            order by customerNumber, row_num
            ) as source
            ON source.customerNumber = target.customerNumber
            WHEN MATCHED AND source.timestamp > target.timestamp THEN UPDATE SET 
                target.timestamp = source.timestamp,
                target.customerNumber = source.customerNumber,
                target.customerName = source.customerName,
                target.contactLastName = source.contactLastName,
                target.contactFirstName = source.contactFirstName,
                target.phone = source.phone,
                target.addressLine1 = source.addressLine1,
                target.addressLine2 = source.addressLine2,
                target.city = source.city,
                target.state = source.state,
                target.postalCode = source.postalCode,
                target.country = source.country,
                target.salesRepEmployeeNumber = source.salesRepEmployeeNumber,
                target.creditLimit = source.creditLimit
            WHEN NOT MATCHED THEN INSERT *
        """)
    
    @task_group(group_id='load_staging')
    def load_staging():
        for table in ls_raw_tables:
            create_staging_task = PythonOperator(
                task_id=f'create_staging_{table}',
                python_callable=create_staging_table,
                op_args=[table, BASE_PATH, RAW]
            )
            create_staging_task

    load_staging()