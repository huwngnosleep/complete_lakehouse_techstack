from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when, to_date, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, LongType, TimestampType, DateType, FloatType

# Define the Kafka topic to read from
kafka_topic = "coor"
ivy2_repository = "/home/spark/"
# Define the schema for your data
schema = StructType([
    StructField("id", StringType(), True),
    StructField("long", FloatType(), True),
    StructField("lat", FloatType(), True),
])

# Create a Spark session
spark = SparkSession.builder \
    .appName("KafkaStreamReader") \
    .config("spark.jars.ivy", ivy2_repository) \
    .enableHiveSupport() \
    .getOrCreate()

# Read data from Kafka
df = (
    spark
    .readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", kafka_topic)
    .option("startingOffsets", "latest")
    .option("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer")
    .load()
)

df = (
    df
    .withColumn("key_str", df["key"].cast("string"))
    .withColumn("value_str", df["value"].cast("string"))
    .withColumn("value_json", from_json(col("value_str"), schema))
)

# Save DataFrame as a Parquet table
# streaming_query = df.writeStream \
#     .format("parquet") \
#     .outputMode("append") \
#     .option("checkpointLocation", "/test/inventory/checkpoint") \
#     .option("path", "/test/inventory") \
#     .start()
# streaming_query.awaitTermination()


# -- DEBUG --
streaming_debug_query = (
    df.writeStream
    .outputMode("append")
    .format("console")
    .start()
)
streaming_debug_query.awaitTermination()

