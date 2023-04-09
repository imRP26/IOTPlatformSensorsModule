import json
from kafka import KafkaProducer
from kafka.errors import KafkaError
from random import randint


producer = KafkaProducer(bootstrap_servers='127.0.0.1:54351', 
                         value_serializer=lambda m: json.dumps(m).encode('ascii'))
kafka_topic = 'otherTeamRequest'


def on_success(metadata):
    print (f"Message produced to topic '{metadata.topic}' at offset {metadata.offset}")


def on_error(e):
    print (f"Error sending message: {e}")


sensor_id = randint(1, 3)
new_value = randint(1, 10)
msg = {'sensor_id' : sensor_id, 'new_value' : new_value}
future = producer.send(kafka_topic, msg)
future.add_callback(on_success)
future.add_errback(on_error)

producer.flush()
producer.close()
