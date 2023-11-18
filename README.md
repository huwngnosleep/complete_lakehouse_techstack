This is a demo of CDC from MySql database into Apache Iceberg table 

# Prerequisites
- Java 8 installation: 
- Kafka 3.6.0 with Scala 2.13 installation:
- Zookeeper 3.9.1 installation:
- Hadoop 3.3.6 installation: https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz 
- Hive 4.0.0 beta 1 installation: https://dlcdn.apache.org/hive/hive-4.0.0-beta-1/apache-hive-4.0.0-beta-1-bin.tar.gz
- MySQL and Adminer installation in docker-compose file


### All commands below are executed under root folder of my project, make sure you are running as SuperUser

# 1, Setup MySQL data source
```
docker-compose -f ./docker-compose/mysql-with-adminer.docker-compose.yml up -d
```

# 2, Setup Zookeeper and Kafka

# 3, Setup Apache Hadoop
install some dependencies for ubuntu
```
sudo apt-get install ssh pdsh
```

Copy all configuration files to $HADOOP_HOME/etc/hadoop
```
cp ./config/hadoop/* $HADOOP_HOME/etc/hadoop
```

Start hdfs
```
$HADOOP_HOME/sbin/start-dfs.sh
```

# 4, Setup Apache Hive

Init schema incase we do not have Hive metastore setup
```
$HIVE_HOME/bin/schematool -dbType derby -initSchema
```

Copy all configuration files to $HIVE_HOME/conf
```
cp ./config/hive/* $HIVE_HOME/conf
```

Start hiveserver2
```
$HIVE_HOME/bin/hiveserver2 
```

Enter beeline CLI to interact with hiveserver2
```
$HIVE_HOME/bin/beeline -u jdbc:hive2://localhost:10000/default
```