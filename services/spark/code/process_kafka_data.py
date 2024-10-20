from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import from_json, col, when, to_date, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, LongType, TimestampType, DateType, FloatType, IntegerType
from pyspark.sql.functions import *

# Define the Kafka topic to read from
SOURCE_KAFKA_TOPIC = "classicmodels.classicmodels.customers"
SINK_KAFKA_TOPIC = "customers_distinct"
ivy2_repository = "/home/spark/"

# Create a Spark session
spark = SparkSession.builder \
    .appName("KafkaStreamReader") \
    .config("spark.jars.ivy", ivy2_repository) \
    .enableHiveSupport() \
    .getOrCreate()

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

df = (
    df
    .withColumn("key", get_json_object(df["key"].cast("string"), '$.customerNumber'))
    .withColumn("customerNumber", get_json_object(df["value"].cast("string"), '$.after.customerNumber'))
    .withColumn("customerName", get_json_object(df["value"].cast("string"), '$.after.customerName'))
    .withColumn("contactLastName", get_json_object(df["value"].cast("string"), '$.after.contactLastName'))
    .withColumn("contactFirstName", get_json_object(df["value"].cast("string"), '$.after.contactFirstName'))
    .withColumn("phone", get_json_object(df["value"].cast("string"), '$.after.phone'))
    .withColumn("addressLine1", get_json_object(df["value"].cast("string"), '$.after.addressLine1'))
    .withColumn("addressLine2", get_json_object(df["value"].cast("string"), '$.after.addressLine2'))
    .withColumn("city", get_json_object(df["value"].cast("string"), '$.after.city'))
    .withColumn("state", get_json_object(df["value"].cast("string"), '$.after.state'))
    .withColumn("postalCode", get_json_object(df["value"].cast("string"), '$.after.postalCode'))
    .withColumn("country", get_json_object(df["value"].cast("string"), '$.after.country'))
    .withColumn("salesRepEmployeeNumber", get_json_object(df["value"].cast("string"), '$.after.salesRepEmployeeNumber'))
    .withColumn("creditLimit", get_json_object(df["value"].cast("string"), '$.after.creditLimit'))
    .drop("value")    
)


# Save DataFrame as a Parquet table
streaming_query = df.writeStream \
    .format("parquet") \
    .outputMode("append") \
    .trigger(processingTime='5 seconds') \
    .option("checkpointLocation", "/checkpoint/classicmodels/customers") \
    .option("path", "/classicmodels/raw/customers") \
    .start()
streaming_query.awaitTermination()

# kafka_sink = df.writeStream \
#     .format("kafka") \
#     .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
#     .option("topic", SINK_KAFKA_TOPIC) \
#     .start()

# -- DEBUG --
# streaming_debug_query = (
#     df.writeStream
#     .outputMode("update")
#     .format("console")
#     .start()
# )
# streaming_debug_query.awaitTermination()

