from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import from_json, col, when, to_date, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, LongType, TimestampType, DateType, FloatType, IntegerType
from pyspark.sql.functions import *

# Define the Kafka topic to read from
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092,kafka_broker_001:9092,kafka_broker_002:9092"
SOURCE_KAFKA_TOPIC = "test"
SINK_KAFKA_TOPIC = "user_click_fact"

# Create a Spark session
IVY2_REPOSITORY = "/home/spark/"
spark = SparkSession.builder \
    .appName("ClickDataEnrichment") \
    .config("spark.jars.ivy", IVY2_REPOSITORY) \
    .config("spark.sql.defaultCatalog", "iceberg") \
    .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog") \
    .enableHiveSupport() \
    .getOrCreate()

# Read data from Kafka
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
        *,
        cast(clicks_processed.customerNumber as string) as key,
        cast(concat(
            clicks_processed.customerNumber,
            ',',
            customer.customerName,
            ',',
            customer.phone,
            ',',
            customer.addressLine1,
            ',',
            customer.addressLine2,
            ',',
            customer.city,
            ',',
            customer.state,
            ',',
            customer.country,
            ',',
            clicks_processed.ip_address,
            ',',
            clicks_processed.col2,
            ',',
            clicks_processed.timestamp,
            ',',
            clicks_processed.http_info,
            ',',
            clicks_processed.method
        ) as binary) as value
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

kafka_sink = df.writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("topic", SINK_KAFKA_TOPIC) \
    .option("checkpointLocation", "/checkpoint/user_clicks") \
    .start()
kafka_sink.awaitTermination()

# -- DEBUG --
# streaming_debug_query = (
#     df.writeStream
#     .outputMode("update")
#     .format("console")
#     .start()
# )
# streaming_debug_query.awaitTermination()

