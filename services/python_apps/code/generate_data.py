import random
import json
from kafka import KafkaProducer, KafkaConsumer
import concurrent.futures
import logging
logging.basicConfig(level=logging.INFO)
from utils import generate_random_coordinates, change_location
producer = KafkaProducer(bootstrap_servers='kafka:9092', client_id="traffic_data_generator", value_serializer=lambda v: json.dumps(v).encode('utf-8'), acks='all')
print(producer.bootstrap_connected())
NUM_VEHICLE = 100

init_coordinates = generate_random_coordinates(NUM_VEHICLE)
print(init_coordinates)


def send_new_messages():
    for i in range(100):
        random_point = f"Point_{random.randint(1, NUM_VEHICLE)}"
        new_location = change_location(init_coordinates, random_point, random.randint(1, 5))
        producer.send('coor', new_location)
        
    producer.flush()


with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
    for i in range(1):    
        executor.submit(send_new_messages)
    