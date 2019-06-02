#!/usr/bin/python3
#
# Reads serial data and uploads to infuxdb
import random
import time
import serial
import json
from influxdb import InfluxDBClient
from squid import *
from datetime import datetime


ser = serial.Serial(
 port='/dev/ttyACM0',
 baudrate = 9600,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=5
)

rgb = Squid(19, 20, 21)

while True:
    rgb.set_color(WHITE)
    client = InfluxDBClient(host='111.222.333.444', port=8888, username='user', password='password', ssl=False, verify_ssl=False)
    client.switch_database("measurement")
    a = datetime.now()
    while(a.second != 58 and a.second != 28):
        time.sleep(.1)
        a = datetime.now()
        ser.reset_input_buffer()
    x = None
    points = []
    data = ""
    rgb.set_color(BLUE)
    x=ser.readline()
    x = x.decode('utf-8')
    stripped = None
    try:
        print("try")
        print(data)
        data = json.loads(x)
        print(data)
        print("datapoint")
    except Exception as e:
        print("exception")
        print(data)
        print(e)
    try:
        print(data)
        print("assignments")
        soil1 = data["Sensors"][0]["soil1"]
        soil2 = data["Sensors"][1]["soil2"]
        soil3 = data["Sensors"][2]["soil3"]
        soil4 = data["Sensors"][3]["soil4"]
        humidity = (data["Sensors"][4]["humidity"])
        temperature = (data["Sensors"][5]["temperature"])
        infraredlight = (data["Sensors"][6]["infraredlight"])
        visiblelight = (data["Sensors"][7]["visiblelight"])
        fullspectrum = (data["Sensors"][8]["fullspectrum"])
        lux = (data["Sensors"][9]["lux"])
        a = datetime.now()
        last = 0
        rgb.set_color(PURPLE)
        while(a.second != 0 and a.second != 30):
            #print("waiting for right time: "+str(a.second))
            time.sleep(.1)
            a = datetime.now()
            last = a.second
        dt_obj = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        print(dt_obj)
        point = {
                    "measurement": 'measurement',
                    "time": dt_obj,
                    "tags": {
                        "section": "section",
                    },
                    "fields": {
                        "soil1": soil1,
                        "soil2": soil2,
                        "soil3": soil3,
                        "soil4": soil4,
                        "humidity": humidity,
                        "temperature": temperature,
                        "infraredlight": infraredlight,
                        "visiblelight": visiblelight,
                        "fullspectrum": fullspectrum,
                        "lux": lux,
                        "date": time.strftime('%d/%m/%Y %H:%M:%S')
                    }
                }

        points.append(point)
        print("writting")
        rgb.set_color(GREEN)
        client.write_points(points, time_precision='ms')
        print("written")
        time.sleep(2)
        rgb.set_color(WHITE)
    except Exception as e:
        print(e)