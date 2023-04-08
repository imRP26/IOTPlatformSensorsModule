import sqlite3


conn = sqlite3.connect('sensors.db')
sensors = [
    "1, 'Sensor1', 'Brightness', '10', '20', '127.0.0.1', '8030', '2023-04-05 09:15:08'", 
    "2, 'Sensor2', 'Temperature', '13', '26', '127.0.0.2', '8032', '2023-04-06 04:13:23'", 
    "3, 'Sensor3', 'Humidity', '15', '80', '127.0.0.3', '8034', '2023-04-07 08:11:35'"
]

for sensor_data in sensors:
    insertCmd = f'INSERT INTO sensor VALUES ({sensor_data})'
    conn.execute(insertCmd)
conn.commit()
