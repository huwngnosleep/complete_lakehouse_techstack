from pyspark.sql import SparkSession

spark = SparkSession \
    .builder \
    .master("spark://localhost:7077") \
    .appName("Python Spark SQL basic example") \
    .config("spark.some.config.option", "some-value") \
    .config("spark.sql.catalogImplementation", "hive") \
    .config("spark.sql.warehouse.dir", "hdfs://172.21.0.1:9000/warehouse") \
    .getOrCreate()

df = spark.read.option("header", True).csv("hdfs://172.21.0.1:9000/test/people.csv")
df.show()

df.createGlobalTempView("people")

sqlDF = spark.sql("SELECT * FROM global_temp.people")
sqlDF.show()

spark.sql("""
          CREATE DATABASE IF NOT EXISTS test;
          """)

spark.sql("""
          CREATE TABLE test.people using hive AS SELECT * FROM global_temp.people
          """)


spark.sql("SELECT * FROM test.people").show()
