from config import app, db
from datetime import datetime
from models import Sensor, Parameters


SENSORS_PARAMETERS = [
    {
        'sensorname' : 'Sensor1', 
        'sensortype' : 'Brightness', 
        'sensorlatitude' : '10', 
        'sensorlongitude' : '20', 
        'sensorip' : '127.0.0.1', 
        'sensorport' : '8030', 
        'parameters' : [
            ('1', 'DUMMY', '2023-04-08 07:15:03'),  
        ], 
    }, 
    {
        'sensorname' : 'Sensor2', 
        'sensortype' : 'Temperature', 
        'sensorlatitude' : '20', 
        'sensorlongitude' : '30', 
        'sensorip' : '127.0.0.2', 
        'sensorport' : '8032', 
        'parameters' : [
            ('2', 'DUMMY', '2023-04-08 00:15:33'),  
        ],
    }, 
    {
        'sensorname' : 'Sensor3', 
        'sensortype' : 'Humidity', 
        'sensorlatitude' : '30', 
        'sensorlongitude' : '40', 
        'sensorip' : '127.0.0.3', 
        'sensorport' : '8034', 
        'parameters' : [
            ('3', 'DUMMY', '2023-04-08 06:45:23'), 
        ],
    }, 
]

with app.app_context():
    db.drop_all()
    db.create_all()
    for data in SENSORS_PARAMETERS:
        new_sensor = Sensor(sensorname=data.get('sensorname'), sensortype=data.get('sensortype'), 
                            sensorlatitude=data.get('sensorlatitude'), sensorlongitude=data.get('sensorlongitude'), 
                            sensorip=data.get('sensorip'), sensorport=data.get('sensorport'))
        for _, content, timestamp in data.get('parameters', []):
            new_sensor.parameters.append(Parameters(content=content, timestamp=datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'), ))
        db.session.add(new_sensor)
        db.session.commit()
