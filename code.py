import time
import board
import json
from analogio import AnalogIn
import busio
import adafruit_si7021
import adafruit_tsl2591
analog_in1 = AnalogIn(board.A0)
analog_in2 = AnalogIn(board.A1)
analog_in3 = AnalogIn(board.A2)
analog_in4 = AnalogIn(board.A3)
# Initialize the I2C bus.
i2c2 = busio.I2C(board.D0, board.D1)
i2c = busio.I2C(board.D2, board.D3)

# Initialize the sensor.
lightsensor = adafruit_tsl2591.TSL2591(i2c)
temphumiditysensor = adafruit_si7021.SI7021(i2c2)
lightsensor.gain = adafruit_tsl2591.GAIN_LOW
lightsensor.integration_time = adafruit_tsl2591.INTEGRATIONTIME_100MS

def get_voltage(pin):
    return (pin.value * 3.3) / 65536

def get_moisture_scale(pin):
    #return abs(((pin.value * 3) / 2000)-100)
    return ((pin.value * 3) / 2000)

while True:
    #soil1, soil2, soil3, soil4, humidity, temperature, infraredlight, visiblelight, fullspectrum, lux
    data = {"Sensors":[{"soil1" : round(get_moisture_scale(analog_in1),1),}, {"soil2" : round(get_moisture_scale(analog_in2),1),}, {"soil3" : round(get_moisture_scale(analog_in2),1),}, {"soil4" : round(get_moisture_scale(analog_in3),1),}, {"humidity" : temphumiditysensor.relative_humidity,}, {"temperature" : (temphumiditysensor.temperature  * 9 / 5 + 32),},  {"infraredlight" : lightsensor.infrared,}, {"visiblelight" : lightsensor.visible,}, {"fullspectrum" : lightsensor.full_spectrum,}, {"lux" : lightsensor.lux,}]}
    jsondata = json.dumps(data)
    print(jsondata)
    time.sleep(.1)
