from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when, to_date, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, LongType, TimestampType, DateType

# Define the Kafka topic to read from
kafka_topic = "kafka-mysql-hung-test.test.inventory"
ivy2_repository = "/home/spark/"
# Define the schema for your data
schema = StructType([
    StructField("before", StructType([
        StructField("id", LongType(), True),
        StructField("userid", LongType(), True),
        StructField("name", StringType(), True),
        StructField("created_date", LongType(), True),
        StructField("modified_date", LongType(), True),
    ]), True),
    StructField("after", StructType([
        StructField("id", LongType(), True),
        StructField("userid", LongType(), True),
        StructField("name", StringType(), True),
        StructField("created_date", LongType(), True),
        StructField("modified_date", LongType(), True),
    ]), True),
    StructField("op", StringType(), True),
    StructField("ts_ms", LongType(), True),
])

# Create a Spark session
spark = SparkSession.builder \
    .appName("KafkaStreamReader") \
    .config("spark.jars.ivy", ivy2_repository) \
    .enableHiveSupport() \
    .getOrCreate()

spark.sql("CREATE DATABASE IF NOT EXISTS test")
spark.sql("DROP TABLE IF EXISTS spark_catalog.test.inventory")
create_table_sql = """CREATE TABLE IF NOT EXISTS spark_catalog.test.inventory (   
                        id BIGINT, 
                        userid BIGINT, 
                        name STRING, 
                        created_date BIGINT, 
                        modified_date BIGINT, 
                        date_timestamp DATE, 
                        payload_ts_ms BIGINT, 
                        operation STRING
                    )
                    USING parquet
                    OPTIONS (
                        'path' '/test/inventory',
                        'delete_data' 'true'
                    )
                """

spark.sql(create_table_sql)


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
    df.selectExpr("key", "value", "timestamp")
    .withColumn("key_str", df["key"].cast("string"))
    .withColumn("value_str", df["value"].cast("string"))
    .withColumn("value_json", from_json(col("value_str"), schema))
    .withColumn(
        "data_capture",
        when(
            col("value_json.op") == "d", col("value_json.before")
        ).otherwise(col("value_json.after")),
    ).withColumn("op", col("value_json.op"))
    .withColumn("operation", when(col("value_json.op") == "c", "INSERT")
                                    .when(col("op") == "u", "UPDATE")
                                    .when(col("op") == "d", "DELETE")
                                    .when(col("op") == "r", "READ")
                                    .otherwise("UNKNOWN"))
    .withColumn("date_timestamp", to_date("timestamp"))
    .withColumn("payload_ts_ms", col("value_json.ts_ms"))
    .selectExpr("data_capture.*", "date_timestamp", "payload_ts_ms", "operation")
)

# Save DataFrame as a Parquet table
streaming_query = df.writeStream \
    .format("parquet") \
    .outputMode("append") \
    .option("checkpointLocation", "/test/inventory/checkpoint") \
    .option("path", "/test/inventory") \
    .start()
streaming_query.awaitTermination()


# -- DEBUG --
# streaming_debug_query = (
#     df.writeStream
#     .outputMode("append")
#     .format("console")
#     .start()
# )
# streaming_debug_query.awaitTermination()

