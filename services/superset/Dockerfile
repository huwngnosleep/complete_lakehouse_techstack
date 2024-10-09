FROM apache/superset

USER root

RUN pip install clickhouse-connect
RUN pip install pyhive thrift sasl

USER superset
