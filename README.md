![stack architecture](architecture.jpg)

# This project implements an end-to-end tech stack for a data platform
follow Data Lake-House architecture, there are main interfaces of this platform: 
- Distributed query/execution engine: Spark Thrift Server
- Stream processing: Kafka
- Storage: HDFS
- Data mart: ClickHouse
- Orchestration: Airflow
- Main file format: Parquet with Snappy compression
- Warehouse table format: Hive and Iceberg

### How-to-run will be uploaded later

# First run:
1. Change the variable IS_RESUME in ./services/metastore/docker-compose.yml to False

2. Grant all permissions for HDFS
```
sudo mkdir -p ./services/hadoop/data
sudo chmod  777 ./services/hadoop/data/*
```

1. Create docker network
`docker network create default_net`

1. Docker up
`bash start_all_service.sh`

After finishing all the above steps, change IS_RESUME back to True then rerun start all service