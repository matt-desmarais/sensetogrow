import network
import machine
import time
import si7021
from machine import RTC
import urequests
import utime
from ntptime import settime
import sys

section = "section"
db = "http://somedomain.com:8086/write?db=sensordata&u=admin&p=password"
led = machine.Pin(16, machine.Pin.OUT)

def do_connect():
    try:
        import network
        sta_if = network.WLAN(network.STA_IF)
        starttime = utime.time()
        if not sta_if.isconnected():
            print('connecting to network...')
            sta_if.active(True)
            sta_if.connect('SSID', 'password')
            while not sta_if.isconnected():
                print(utime.time() - starttime)
                if((utime.time() - starttime) > 20):
                    machine.reset()
                pass
        print('network config:', sta_if.ifconfig())
        settime()
        #print("set time")
    except Exception as e:
        print('Error: {}'.format(e))

i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4), freq=400000)

temp_sensor = si7021.Si7021(i2c)

while True:
    try:
        do_connect()
        if(utime.localtime()[5]==0):
            humi = temp_sensor.relative_humidity
            temp = si7021.convert_celcius_to_fahrenheit(temp_sensor.temperature)
            print('Relative Humidity:   {value}'.format(value=temp_sensor.relative_humidity))
            print('Fahrenheit:          {value}'.format(value=si7021.convert_celcius_to_fahrenheit(temp_sensor.temperature)))
            resp_data = 'data,section={0} temperature={1} \n data,section={0} humidity={2}'.format(section,temp,humi)
            resp = urequests.post(db, data=resp_data)
            print('response: {}'.format(resp.status_code))
            if resp.status_code == 204:
                print("upload ok")
                led.off()
            else:
                print("upload error")
                led.off()
                time.sleep(.2)
                led.on()
                time.sleep(.2)
                led.off()
                time.sleep(.2)
                led.on()
                time.sleep(.2)
                led.off()
                time.sleep(.2)
                led.on()
            time.sleep(1)
            led.on()
        else:
            time.sleep(.5)
            
    except Exception as e:
        print('Error: {}'.format(e))
