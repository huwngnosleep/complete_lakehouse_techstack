from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType

# Define the Kafka topic to read from
kafka_topic = "kafka-mysql-hung-test.test.inventory"
ivy2_repository = "/home/spark/"
# Define the schema for your data
schema = StructType([
    StructField("key", StringType(), True),
    StructField("value", StringType(), True),
])

# Create a Spark session
spark = SparkSession.builder \
    .appName("KafkaStreamReader") \
    .config("spark.jars.ivy", ivy2_repository) \
    .getOrCreate()

# Read data from Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "172.21.0.1:9092") \
    .option("subscribe", kafka_topic) \
    .load()
    
df.selectExpr("CAST(value AS STRING)")

query = (
    df.writeStream
    .outputMode("append")
    .format("console")
    .start()
)

query.awaitTermination()
