import sqlite3


conn = sqlite3.connect('sensors.db')
columns = ['id INTEGER PRIMARY KEY', 
           'sensorname VARCHAR UNIQUE', 
           'sensortype VARCHAR', 
           'sensorlatitude VARCHAR', 
           'sensorlongitude VARCHAR', 
           'sensorip VARCHAR', 
           'sensorport VARCHAR', 
           'timestamp DATETIME', ]

createTableCmd = f"CREATE TABLE sensor ({','.join(columns)})"
conn.execute(createTableCmd)
