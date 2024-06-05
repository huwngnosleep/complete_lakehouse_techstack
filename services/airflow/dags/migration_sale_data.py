import os
from datetime import datetime
from airflow import DAG
import pandas
import pymssql
DAG_ID = "migration_sale_data"
with DAG(
    DAG_ID,
    schedule=None,
    start_date=datetime(2021, 10, 1),
    catchup=False,
) as dag:
    @dag.task(task_id="get_raw_data")
    def get_raw_data():
        conn = pymssql.connect('mssql:1433', 'sa', 'root@@@123', "retail")
        data = pandas.read_sql("SELECT * FROM sales.orders;", conn)
        print("data", data)
        conn.close()
    get_raw_data()