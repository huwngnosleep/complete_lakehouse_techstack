from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import from_json, col, when, to_date, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, LongType, TimestampType, DateType, FloatType, IntegerType
from pyspark.sql.functions import *

# Define the Kafka topic to read from
SOURCE_KAFKA_TOPIC = "test"
# SINK_KAFKA_TOPIC = "customers_distinct"
ivy2_repository = "/home/spark/"

# Create a Spark session
spark = SparkSession.builder \
    .appName("KafkaStreamReader") \
    .config("spark.jars.ivy", ivy2_repository) \
    .config("spark.sql.defaultCatalog", "iceberg") \
    .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog") \
    .enableHiveSupport() \
    .getOrCreate()

print("current_catalog", spark.catalog.currentCatalog())
# Read data from Kafka

KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
df = (
    spark
    .readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
    .option("subscribe", SOURCE_KAFKA_TOPIC)
    .option("startingOffsets", "latest")
    .load()
)

df.createOrReplaceTempView("clicks")

df = spark.sql("""
    with clicks_processed as (
    select 
        cast(value as String) as valueString,
        get_json_object(cast(value as String), '$.message') as message,
        split(message, '-') as splitted_message,
        element_at(splitted_message, 1) as ip_address,
        element_at(splitted_message, 2) as col2,
        element_at(splitted_message, 3) as timestamp,
        element_at(splitted_message, 4) as http_info,
        element_at(splitted_message, 5) as method,
        CAST(rand() * (10000100 - 10000001 + 1) + 10000001 AS INT) AS customerNumber
    from clicks
    )
    select 
        *
    from clicks_processed
    left JOIN classicmodels_warehouse.customers customer on clicks_processed.customerNumber = customer.customerNumber
    """)


# Save DataFrame as a Parquet table
# streaming_query = df.writeStream \
#     .format("parquet") \
#     .outputMode("append") \
#     .trigger(processingTime='5 seconds') \
#     .option("checkpointLocation", "/checkpoint/classicmodels/customers") \
#     .option("path", "/classicmodels/raw/customers") \
#     .start()
# streaming_query.awaitTermination()

# kafka_sink = df.writeStream \
#     .format("kafka") \
#     .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
#     .option("topic", SINK_KAFKA_TOPIC) \
#     .start()

# -- DEBUG --
streaming_debug_query = (
    df.writeStream
    .outputMode("update")
    .format("console")
    .start()
)
streaming_debug_query.awaitTermination()

