import sqlite3


conn = sqlite3.connect('sensors.db')
cur = conn.cursor()
cur.execute('SELECT * FROM sensor')

sensors = cur.fetchall()
for sensor in sensors:
    print (sensor)
