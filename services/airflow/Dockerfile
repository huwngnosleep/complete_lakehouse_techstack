FROM apache/airflow:2.9.1
USER airflow
# dependencies to run dags
COPY dependencies/hadoop-3.4.0 /hadoop
COPY dependencies/jdk-23 /java
COPY requirements.txt requirements.txt
ENV JAVA_HOME=/java
RUN pip install -r requirements.txt
