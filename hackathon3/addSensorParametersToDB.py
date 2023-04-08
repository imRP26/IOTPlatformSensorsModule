from config import app, db
from datetime import datetime
from models import Sensor, Parameters, parameters_schema
from random import randint
import requests
from time import sleep
import xmltodict


om2m_url = 'http://127.0.0.1:5089/'
om2m_username = 'admin'
om2m_password = 'admin'
om2m_csebase = '~/in-cse/'
om2m_resource_path = 'in-name/AE-TEST/Node-1/Data/la'
om2m_auth = requests.auth.HTTPBasicAuth(om2m_username, om2m_password)
sensor_types = ['Brightness', 'Humidity', 'Temperature']

with app.app_context():
    while True:
        om2m_response = requests.get(om2m_url + om2m_csebase + om2m_resource_path, auth=om2m_auth)
        timestamp = datetime.now().replace(microsecond=0).isoformat(' ')
        dict_obj = xmltodict.parse(om2m_response.text)
        data = dict_obj['m2m:cin']
        sensor_id = randint(1, 3)
        #sensor = Sensor.query.get(sensor_id)
        sensor = db.session.get(Sensor, sensor_id)
        parameter = {'content' : str(data), 'sensor_id' : sensor_id}
        new_parameter = parameters_schema.load(parameter, session=db.session)
        sensor.parameters.append(new_parameter)
        db.session.commit()
        sleep(5)
