from config import app, db
from datetime import datetime
#from heartBeat import heart_beat
import json
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from models import Node, Parameters, parameters_schema
from random import randint
import requests
import threading
from time import sleep


'''
Message on KAFKA Push success
'''
def onSuccess(metadata):
    print(f"Message produced to topic '{metadata.topic}' at offset {metadata.offset}")


'''
Message on KAFKA Push Error
'''
def onError(e):
    print(f"Error sending message: {e}")


'''
Initial filling of the latest instance of data for all the nodes
'''
def initializeAllNodes():
    producer = KafkaProducer(bootstrap_servers = "127.0.0.1:53471", 
                             value_serializer=lambda m: json.dumps(m).encode('ascii'))
    # The list of sensor-types is pre-decided
    sensor_types = ['PM10', 'Temperature', 'AQI', 'pH', 'Pressure', 'Occupancy', \
                    'Current', 'Frequency', 'Light_Status']
    for sensor_type in sensor_types:
        om2m_url1 = 'https://iudx-rs-onem2m.iiit.ac.in/resource/nodes/' + sensor_type
        node_list = requests.get(om2m_url1).json()['results']
        for node in node_list:
            om2m_url2 = 'https://iudx-rs-onem2m.iiit.ac.in/resource/descriptor/' + node
            node_dict = requests.get(om2m_url2).json()
            try:
                node_name = node_dict['Node ID']
                node_latitude = node_dict['Node Location']['Latitude']
                node_longitude = node_dict['Node Location']['Longitude']
                node_parameter_type = sensor_type
                node_ip = '192.168.36.' + str(randint(10, 50))
                node_port = randint(8000, 9000)
                dt_iso = datetime.now().isoformat()
                dot_index = dt_iso.index('.')
                dt_iso = dt_iso[:dot_index] + 'Z'
                om2m_url3 = 'https://iudx-rs-onem2m.iiit.ac.in/channels/' + node_id + '/feeds?start=' + dt_iso
                node_data_dict = requests.get(om2m_url3).json()
                node_parameter_value = randint(20, 40)
                if 'channel' in node_data_dict:
                    node_parameter_fields = node_data_dict['channel']
                    node_parameter_field = None
                    for node_parameter in node_parameter_fields:
                        if node_data_dict[node_parameter] == sensor_type:
                            node_parameter_field = node_parameter
                            break
                    temp_value = node_data_dict['feeds'][0][node_parameter_field]
                    if not isinstance(temp_value, str):
                        node_parameter_value = temp_value
                with app.app_context():
                    #db.drop_all()
                    db.create_all()
                    new_node = Node(nodename=node_name, nodetype=sensor_type, nodelatitude=node_latitude, 
                                    nodelongitude=node_longitude, nodeip=node_ip, nodeport=node_port)
                    content_dict = {}
                    content_dict[sensor_type] = node_parameter_value
                    new_node.parameters.append(Parameters(content=str(content_dict), \
                                               timestamp=datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'), ))
                    parameter = {'content' : str(content_dict), 'node_name' : node_name}
                    kafka_topic = node_name
                    future = producer.send(kafka_topic, parameter)
                    future.add_callback(onSuccess)
                    future.add_errback(onError)
                    db.session.add(new_node)
                    db.session.commit()
            except Exception as e:
                continue


'''
Addition of Data to local SQLITE3 DB 
'''
def addDataToDB():
    producer = KafkaProducer(bootstrap_servers = "127.0.0.1:53471", 
                             value_serializer=lambda m: json.dumps(m).encode('ascii'))
    consumer = KafkaConsumer(bootstrap_servers=["127.0.0.1:53471"], group_id="demo-group", 
                             auto_offset_reset="earliest", enable_auto_commit=False,
                             consumer_timeout_ms=1000, 
                             value_deserializer=lambda m: json.loads(m.decode('ascii')))
    # The list of sensor-types is pre-decided
    sensor_types = ['PM10', 'Temperature', 'AQI', 'pH', 'Pressure', 'Occupancy', \
                    'Current', 'Frequency', 'Light_Status']
    active_nodes = []
    external_request_topic = 'action_device' # Fixed by the Action Manager Module
    action_manager_module_info = []
    while True: 
        node_info = json.loads(requests.get('http://127.0.0.1:8046/api/nodes').text)
        for node in node_info:
            active_nodes.append((node['id'], node['nodename']))
        for active_node_id, active_node_name in active_nodes:
            kafka_topic = active_node_name
            dt_iso = datetime.now().isoformat()
            dot_index = dt_iso.index('.')
            dt_iso = dt_iso[:dot_index] + 'Z'
            om2m_url = 'https://iudx-rs-onem2m.iiit.ac.in/channels/' + active_node_name + '/feeds?start=' + dt_iso
            try:
                node_data_dict = requests.get(om2m_url).json()
                node_parameter_value = randint(20, 40)
                if 'channel' in node_data_dict:
                    node_parameter_fields = node_data_dict['channel']
                    node_parameter_field = None
                    for node_parameter in node_parameter_fields:
                        if node_data_dict[node_parameter] == sensor_type:
                            node_parameter_field = node_parameter
                            break
                    temp_value = node_data_dict['feeds'][0][node_parameter_field]
                    if not isinstance(temp_value, str):
                        node_parameter_value = temp_value
                node = db.session.get(Node, active_node_id)
                consumer.subscribe(external_request_topic)
                # from the other team -> user_id, device_id, new_value
                for msg in consumer:
                    print ('Message received from the Action Manager Module ->', msg.value)
                    user_id, nid, new_value = msg.value['user_id'], msg.value['device_id'], msg.value['new_value']
                    action_manager_module_info.append([nid, new_value])
                for i in range(len(action_manager_module_info)):
                    if new_info[0] == active_node_id:
                        node_parameter_value = new_value
                content_dict = {}
                content_dict[sensor_type] = node_parameter_value
                parameter = {'content' : str(data), 'node_id' : active_node_id}
                future = producer.send(kafka_topic, parameter)
                future.add_callback(onSuccess)
                future.add_errback(onError)
                new_parameter = parameters_schema.load(parameter, session=db.session)
                node.parameters.append(new_parameter)
                db.session.commit()
                sleep(5)
            except Exception as e:
                print ('Erroneous Data!!')
                continue
    producer.flush()
    producer.close()
        

'''
The controller function of the script that calls the desired functions
'''
def main():
    initializeAllNodes()
    addDataToDB()


if __name__ == '__main__':
    main()
