#!/bin/bash

echo "START LOADING VARIABLE..."
cat /etc/environment
source /etc/environment

echo "kafka.service: ## Starting ##" 

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "try restarting kafka.service: timestamp ${TIMESTAMP}"

${KAFKA_HOME}/bin/zookeeper-server-start.sh -daemon ${KAFKA_HOME}/config/zookeeper.properties
${KAFKA_HOME}/bin/kafka-server-start.sh -daemon ${KAFKA_HOME}/config/server.properties
${HADOOP_HOME}/sbin/start-dfs.sh

