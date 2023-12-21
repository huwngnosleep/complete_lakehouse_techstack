#!/bin/bash


# Use the ls command to get a list of files in the current directory
dirs=$(ls ./services)

# Loop through each file in the list
for sub_dir in $dirs; do
    docker compose -f ./services/$sub_dir/docker-compose.yml up -d
done

# print all container and ips
echo RUNNING CONTAINERS:

docker inspect -f '{{index (split .Name "/") 1}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -aq)
