#!/bin/bash
# initilized=0
# if [ -f "first_run" ]; then
#     echo "File exists. Reading content:"
#     first_run=$(cat "first_run")
#     if [[ $first_run == "hello" ]]; then
#         initilized=1
#         echo Initialize completed, docker upping now...
#     else
#         echo First run, initalizing...
#     fi
# else
#     echo first_run = true > first_run
#     echo "File 'first_run' does not exist."
# fi

# Use the ls command to get a list of files in the current directory
dirs=$(ls ./services)

# Loop through each file in the list
for sub_dir in $dirs; do
    docker compose -f ./services/$sub_dir/docker-compose.yml up -d
done

# print all container and ips
echo RUNNING CONTAINERS:

docker inspect -f '{{index (split .Name "/") 1}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -aq)
