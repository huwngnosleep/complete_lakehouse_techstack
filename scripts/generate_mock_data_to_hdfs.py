from pyhive import hive
import random
from faker import Faker
fake = Faker()
from datetime import datetime, date, timedelta
import tempfile
from sqlalchemy import *
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import *
import pandas as pd
import uuid
import os
import subprocess
import time

NUM_RECORDS_EACH_DATAFRAME = 1000000
NUM_DATAFRAMES = 10

def random_date(start_year=2020, end_year=2024):
    """
    This function generates a random date between the specified start and end years (inclusive).

    Args:
        start_year (int, optional): The starting year for random date generation. Defaults to 1900.
        end_year (int, optional): The ending year for random date generation. Defaults to 2024.

    Returns:
        date: A random date between the start and end years.
    """
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)

    day_count = (end_date - start_date).days + 1

    random_day = random.randint(0, day_count - 1)

    random_date = start_date + timedelta(days=random_day)

    return random_date


def generate_data(num_rows: int) -> pd.DataFrame:
    data = []
    categories = [fake.name(), fake.name(), fake.name()]
    for i in range(num_rows):
        product_id = i
        product_name = fake.name()
        category = random.choice(categories)
        price = random.uniform(0.0, 10000000000.0)
        created_date = random_date()
        
        # data.append((product_id, product_name, category, price, created_date))
        data.append({
            "product_id": product_id, 
            "product_name": product_name, 
            "category": category, 
            "price": price, 
            "created_date": created_date
        })
    return pd.DataFrame(data)


# Hive connection details (replace with yours)
host = "localhost"
port = 10000
username = None
password = None
database = "default" 

conn = hive.connect(host)
cursor = conn.cursor()
cursor.execute('SELECT 1')
print(cursor.fetchone())

hive_table_name = "product_hive"
iceberg_table_name = "product_iceberg"
RAW_FILE_PATH = f"/test/raw/{hive_table_name}"
RAW_FILE_PATH_TMP = RAW_FILE_PATH + "/tmp"

engine = create_engine('hive://localhost:10000/default')

# Define table schema 
create_table_command = f"""
    CREATE TABLE IF NOT EXISTS default.{hive_table_name} (
        product_id int COMMENT 'Unique identifier for the product',
        product_name string COMMENT 'Name of the product',
        category string COMMENT 'Category of the product',
        price double COMMENT 'Price of the product',
        created_date date
    )
    USING parquet
    PARTITIONED BY (created_date)
    LOCATION '/test/{hive_table_name}';
"""

cursor.execute(create_table_command)
   
create_iceberg_table_command = f"""
    CREATE TABLE IF NOT EXISTS iceberg.test_iceberg.{iceberg_table_name} (
        product_id int,
        product_name string,
        category string,
        price double,
        created_date date
    )
    USING iceberg
    PARTITIONED BY (created_date)
    LOCATION '/test/{hive_table_name}';
"""

cursor.execute(create_iceberg_table_command)
    
# clear data dir before loading
subprocess.run(f"bash /opt/hadoop/bin/hdfs dfs -rm -r -f hdfs://localhost:9000{RAW_FILE_PATH_TMP}", shell=True)
subprocess.run(f"bash /opt/hadoop/bin/hdfs dfs -mkdir -p hdfs://localhost:9000{RAW_FILE_PATH_TMP}", shell=True)
for i in range(0, NUM_DATAFRAMES):
    data = generate_data(NUM_RECORDS_EACH_DATAFRAME)
    print(data)
    tmp_file = tempfile.NamedTemporaryFile()
    data.to_parquet(tmp_file.name, compression='snappy')
    os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"
    subprocess.run(f'bash /opt/hadoop/bin/hdfs dfs -put -f {tmp_file.name} hdfs://localhost:9000{RAW_FILE_PATH}{tmp_file.name}.snappy.parquet', shell=True)

# load raw data into staing layer
cursor.execute(f"DROP TABLE IF EXISTS default.tmp_{hive_table_name}")

create_tmp_table_command = f"""
    CREATE TABLE IF NOT EXISTS default.tmp_{hive_table_name}
    USING parquet
    LOCATION '{RAW_FILE_PATH_TMP}/*.snappy.parquet';
"""
cursor.execute(create_tmp_table_command)
cursor.execute(f"SELECT COUNT(*) FROM default.tmp_{hive_table_name}")
print("INSERTED TABLE COUNT", cursor.fetchone())

# insert data into HIVE table
cursor.execute(f"""INSERT INTO default.{hive_table_name} SELECT * FROM default.tmp_{hive_table_name}""")

# insert data into ICEBERG table
cursor.execute(f"""INSERT INTO iceberg.test_iceberg.{iceberg_table_name} SELECT * FROM default.tmp_{hive_table_name}""")

# truncate data when finish testing
cursor.execute(f"""DROP TABLE IF EXISTS default.{hive_table_name}""")
cursor.execute(f"""DROP TABLE IF EXISTS iceberg.test_iceberg.{iceberg_table_name}""")