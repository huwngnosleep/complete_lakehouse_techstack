#!/bin/bash

while true; do
    bash $SPARK_HOME/sbin/start-thriftserver.sh --master spark://spark-master:7077 --properties-file $SPARK_HOME/conf/spark-thriftserver.properties

    # Add a delay between retries to avoid excessive requests
    sleep 30
done