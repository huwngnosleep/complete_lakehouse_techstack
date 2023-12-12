#!/bin/bash

# Function to check if curl request is successful (returns 2xx status code)
check_curl_success() {
    local url=$1
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" $url)
    if [ "$response_code" -ge 200 ] && [ "$response_code" -lt 300 ]; then
        return 0  # Success
    else
        return 1  # Failure
    fi
}

while true; do
    # Make a request to localhost:8080
    if check_curl_success "http://spark-master:8080"; then
        echo "Curl request to localhost:8080 was successful!"
        # Replace the following line with your actual command
        bash $SPARK_HOME/sbin/start-thriftserver.sh --master spark://spark-master:7077 --properties-file $SPARK_HOME/conf/spark-thriftserver.properties
        # break
    else
        echo "Curl request to localhost:8080 failed! Retrying..."
    fi

    # Add a delay between retries to avoid excessive requests
    sleep 30
done
