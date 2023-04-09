import ast
from config import app, db
from datetime import datetime
import json
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from models import Sensor, Parameters, parameters_schema
from random import randint
import requests
from time import sleep
import xmltodict


def on_success(metadata):
  print(f"Message produced to topic '{metadata.topic}' at offset {metadata.offset}")


def on_error(e):
  print(f"Error sending message: {e}")


om2m_url = 'http://127.0.0.1:5089/'
om2m_username = 'admin'
om2m_password = 'admin'
om2m_csebase = '~/in-cse/'
om2m_resource_path = 'in-name/AE-TEST/Node-1/Data/la'
om2m_auth = requests.auth.HTTPBasicAuth(om2m_username, om2m_password)
sensor_types = ['Brightness', 'Humidity', 'Temperature']
producer = KafkaProducer(bootstrap_servers = "127.0.0.1:54351", 
                         value_serializer=lambda m: json.dumps(m).encode('ascii'))
consumer = KafkaConsumer(bootstrap_servers=["127.0.0.1:54351"], group_id="demo-group",
                         auto_offset_reset="earliest", enable_auto_commit=False,
                         consumer_timeout_ms=1000, 
                         value_deserializer=lambda m: json.loads(m.decode('ascii')))
external_request_topic = 'otherTeamRequest'

with app.app_context():
    while True:
        om2m_response = requests.get(om2m_url + om2m_csebase + om2m_resource_path, auth=om2m_auth)
        timestamp = datetime.now().replace(microsecond=0).isoformat(' ')
        dict_obj = xmltodict.parse(om2m_response.text)
        data = dict_obj['m2m:cin']
        sensor_id = randint(1, 3)
        kafka_topic = str(sensor_id)
        sensor = db.session.get(Sensor, sensor_id)
        consumer.subscribe(external_request_topic)
        temp_list = ast.literal_eval(data['con'])
        for msg in consumer:
            temp_list[2] = msg.value['new_value']
            data['con'] = str(temp_list)
            print (data)
        parameter = {'content' : str(data), 'sensor_id' : sensor_id}
        future = producer.send(kafka_topic, parameter)
        future.add_callback(on_success)
        future.add_errback(on_error)
        new_parameter = parameters_schema.load(parameter, session=db.session)
        sensor.parameters.append(new_parameter)
        db.session.commit()
        sleep(5)

producer.flush()
producer.close()
