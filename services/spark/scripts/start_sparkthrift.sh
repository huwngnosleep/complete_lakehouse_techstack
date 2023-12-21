#!/bin/bash
source ../.env
echo SPARK MASTER $SPARK_MASTER_HOST:$SPARK_MASTER_PORT
while true; do
    bash $SPARK_HOME/sbin/start-thriftserver.sh --master spark://$SPARK_MASTER_HOST:$SPARK_MASTER_PORT --properties-file $SPARK_HOME/conf/spark-thriftserver.properties

    sleep 30
done