from pyspark.sql import SparkSession

spark = SparkSession \
    .builder \
    .master("spark://spark-master:7077") \
    .appName("Python Spark SQL basic example") \
    .enableHiveSupport() \
    .getOrCreate()

# spark.sql("DROP TABLE IF EXISTS default.test")

# spark.sql("""
#         CREATE TABLE IF NOT EXISTS default.test (name STRING) 
#         USING hive
#         """)
# spark.sql("LOAD DATA INPATH '/test/people2/*.snappy.parquet' INTO TABLE default.test")

df = spark.sql("SELECT * FROM default.test")
df.show()   