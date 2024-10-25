from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='kafka:9092')
for _ in range(100):
    record_response = producer.send('test', b'test')
    result = record_response.get(timeout=5)
    print(result)