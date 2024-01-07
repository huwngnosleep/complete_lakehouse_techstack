#!/bin/bash
echo SPARK_MASTER - $SPARK_MASTER
while true; do
    std_out=$(bash $SPARK_HOME/sbin/start-thriftserver.sh \
        --master $SPARK_MASTER \
        --properties-file $SPARK_HOME/conf/spark-thriftserver.properties) 
        
    tail -f $std_out
    # sleep 30
done