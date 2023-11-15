#!/bin/bash

echo "kafka.service: ## Starting ##" 

while :
do
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "try restarting kafka.service: timestamp ${TIMESTAMP}"
bash /opt/kafka_2.13-3.6.0/bin/zookeeper-server-start.sh -daemon /opt/kafka_2.1>
bash /opt/kafka_2.13-3.6.0/bin/kafka-server-start.sh -daemon /opt/kafka_2.13-3.>
sleep 60
done