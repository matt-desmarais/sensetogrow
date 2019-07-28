import serial
from squid import *
import json
import os
import math
import random
import time
import datetime
from influxdb import InfluxDBClient
import http.client, urllib
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
import atexit
import csv

ser = serial.Serial(
 port='/dev/ttyACM0',
 baudrate = 9600,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=5
)

rgb = Squid(16, 19, 20)
# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT(addr=0x60)

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)

pump1 = mh.getMotor(1)
pump1.setSpeed(255)
pump2 = mh.getMotor(2)
pump2.setSpeed(255)
pump3 = mh.getMotor(3)
pump3.setSpeed(255)
pump4 = mh.getMotor(4)
pump4.setSpeed(255)

client = InfluxDBClient(host='111.222.333.444', timeout=1, retries=1, port=8086, username='admin',  password='password', ssl=False, verify_ssl=False)
client.switch_database("v2data") 

#sendPushNotification
#input: message (string)
#sends push notification with given message
def sendPushNotification(message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.parse.urlencode({
        "token": "token here",
        "user": "user here",
        "message": message,
      }), { "Content-type": "application/x-www-form-urlencoded" })
    print(conn.getresponse())

#sendPushNotification
#input: message (string)
#sends push notification with given message
def sendAlertPushNotification(message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.parse.urlencode({
        "token": "token here",
        "user": "user here",
        "message": message,
      }), { "Content-type": "application/x-www-form-urlencoded" })
    print(conn.getresponse())


#queryDataMinutes
#input: minutes (int)
#return all results for a given time period
def queryDataMinutes(minutes):
    results = client.query('select * from data ORDER BY "time" DESC limit '+str(minutes))
    return results

#queryDataField
#input: field name (string), minutes (int)
#returns single field for given time period
def queryDataField(datafield, minutes):
    results = client.query('select '+str(datafield)+' from data ORDER BY "time" DESC limit '+str(minutes))
    return results

#queryDataAverage
#input: field name (string), minutes (int)
#returns average for datafield for given time period
def queryDataAverage(datafield, minutes):
    total = 0
    results = client.query('select '+str(datafield)+' from data ORDER BY "time" DESC limit '+str(minutes))
    for p in results.get_points():
        value = p[str(datafield)]
        total = total + value
    average = total/minutes
    print(str(datafield)+" average over "+str(minutes)+" min: "+str(average))
    return average

#queryDataMin
#input: field name (string), minutes (int)
#returns minimum value for datafield for given time period
def queryDataMin(datafield, minutes):
    min = 999999999999999
    results = client.query('select '+str(datafield)+' from data ORDER BY "time" DESC limit '+str(minutes))
    for p in results.get_points():
        value = p[str(datafield)]
        if(min > value):
            min = value
    print(str(datafield)+" minimum over "+str(minutes)+" min: "+str(min))
    return min

#queryDataMax
#input: field name (string), minutes (int)
#returns maximum value for datafield for given time period
def queryDataMax(datafield, minutes):
    max = 0
    results = client.query('select '+str(datafield)+' from data ORDER BY "time" DESC limit '+str(minutes))
    for p in results.get_points():
        value = p[str(datafield)]
        if(max < value):
            max =  value
    print(str(datafield)+" maximum over "+str(minutes)+" min: "+str(max))
    return max

#getLastValue
#input: field name (string)
#returns last value for datafield
def getLastValue(datafield):
    results = client.query('select '+str(datafield)+' from data ORDER BY "time" DESC limit 1')
    for p in results.get_points():
        value = p[str(datafield)]
    #print(str(datafield)+" last value: "+str(value))
    return value


#isFieldBelowPercentage
#input: datafield (string), minutes (int), threshold (int)
#returns pecentage of total time that field is below the threshold
def isFieldBelowPercentage(datafield, minutes, threshold):
   # countAbove = 0
    countBelow = 0
    results = client.query('select '+str(datafield)+' from data ORDER BY "time" DESC limit '+str(minutes))
    for p in results.get_points():
        value = p[str(datafield)]
        if value < threshold:
            countBelow = countBelow + 1
   #     if value > threshold:
   #         countAbove = countAbove + 1
    #print(str(datafield)+" below "+str(threshold)+": "+str(countBelow/minutes)+"% of the time for the last "+str(minutes)+" min")
    #print(str(datafield)+" above "+str(threshold)+": "+str(countAbove/minutes)+"% of the time for the last "+str(minutes)+" min")
    print(str(datafield)+" has been below "+str(threshold)+": for over "+str(minutes)+" min "+str(countBelow/minutes)+"% of the time")
    return countBelow/minutes

#isFieldBelowPercentage
#input: datafield (string), minutes (int), threshold (int)
#returns pecentage of total time that field is below the threshold
def isFieldAbovePercentage(datafield, minutes, threshold):
    countAbove = 0
    #countBelow = 0
    results = client.query('select '+str(datafield)+' from data ORDER BY "time" DESC limit '+str(minutes))
    for p in results.get_points():
        value = p[str(datafield)]
        #if value < threshold:
        #    countBelow = countBelow + 1
        if value > threshold:
            countAbove = countAbove + 1
    #print(str(datafield)+" below "+str(threshold)+": "+str(countBelow/minutes)+"% of the time for the last "+str(minutes)+" min")
    #print(str(datafield)+" above "+str(threshold)+": "+str(countAbove/minutes)+"% of the time for the last "+str(minutes)+" min")
    print(str(datafield)+" has been below "+str(threshold)+": for over "+str(minutes)+" min "+str(countAbove/minutes)+"% of the time")
    return countAbove/minutes


#isFieldBelow
#input: datafield (string), minutes (int), threshold (int)
#returns true/false if the given field and time range is below the threshold
def isFieldBelow(datafield, minutes, threshold):
    results = client.query('select '+str(datafield)+' from data ORDER BY "time" DESC limit '+str(minutes))
    for p in results.get_points():
        value = p[str(datafield)]
        if value > threshold:
            print(str(datafield)+" has NOT been below: "+str(threshold)+" for over "+str(minutes/2)+" min "+str(getLastValue(str(datafield)))[:4])
            return False
    print(str(datafield)+" has been below: "+str(threshold)+" for over "+str(minutes/2)+" min "+str(getLastValue(str(datafield)))[:4])
    return True

#isFieldAbove
#input: datafield (string), minutes (int), threshold (int)
#returns true/false if the given field and time range is above the threshold
def isFieldAbove(datafield, minutes, threshold):
    results = client.query('select '+str(datafield)+' from data ORDER BY "time" DESC limit '+str(minutes))
    for p in results.get_points():
        value = p[str(datafield)]
        if value < threshold:
            print(str(datafield)+" has NOT been above: "+str(threshold)+" for over "+str(minutes)+" min "+str(getLastValue(str(datafield)))[:4])
            return False
    print(str(datafield)+" has been above: "+str(threshold)+" for over "+str(minutes)+" min "+str(getLastValue(str(datafield)))[:4])
    return True


def queryWaterCount(datafield, minutes):
    value = 0
    results = client.query('select sum('+str(datafield)+') from water limit '+str(minutes))
    for p in results.get_points():
        value = p["sum"]
    return value

#returns time plus 1 min
def add1Min(addtotime):
    return addtotime + datetime.timedelta(minutes=1)

#returns time plus given offset
def addMinutes(addtotime, minutes):
    return addtotime + datetime.timedelta(minutes=minutes)



#creates watering schedule for up to 1 minute run time spaced out by equal time periods
def wateringTimes1minLight(totalWater, segmentsperminute):
    #maxWaterPerDayMl = 1220
    pumpRatePerMinMl = 100
    numMinutesToWater = totalWater/pumpRatePerMinMl
    hours = lightoff - lighton
    waterRate = (60*24)/numMinutesToWater
    waterTimes = []
    count = 0
    #get today, set start and end of day
    pub_date = datetime.date.today()
    startofday = datetime.datetime.combine(pub_date, datetime.time.min)
    endofday = datetime.datetime.combine(pub_date, datetime.time.max)
    #waterTime = startofday
    waterTimes = []
    expectedSize = numMinutesToWater * 10
    #segmentsperminute = segments #math.floor(numMinutesToWater/24)
    print("segmentsperminute: "+str(segmentsperminute))
    #calculate minutes per hour to water
    minutesPerHour = (((numMinutesToWater)/hours)*10)
    print("minutesPerHour: "+str(minutesPerHour))
    offsetRate = math.floor((segmentsperminute*(60/minutesPerHour)))
    print("offset rate: "+str(offsetRate))
    waterTime = startofday + datetime.timedelta(hours=lighton) #+ datetime.timedelta(minutes=(offsetRate))
    #while watertime is less than the end of the day minus offset
    while waterTime < (endofday - datetime.timedelta(hours=(24-lightoff), minutes=(offsetRate))):
        #currentWaterTimeMin = waterTime
        #watertime equals (last) watertime plus offset
        waterTime = waterTime + datetime.timedelta(minutes=offsetRate)
        #replace seconds with zeros for time comparison
        waterTime = waterTime.replace(second=0, microsecond=0)
        #add watertime to list of watertimes
        waterTimes.append(waterTime)
        tempTime = waterTime
        for x in range(1, segmentsperminute):
            tempTime = tempTime + datetime.timedelta(seconds=6)
            waterTimes.append(tempTime)
    
    counter = 1
    while expectedSize > len(waterTimes):
        if(expectedSize - len(waterTimes) == 1):
            waterTimes.append(startofday + datetime.timedelta(hours=lighton))
        else:
            addedTime = (startofday + datetime.timedelta(hours=lighton)) + datetime.timedelta(seconds=6*counter)
            waterTimes.append(addedTime)
            #addedTime = (startofday + datetime.timedelta(hours=(lightoff)) - datetime.timedelta(seconds=6*counter))
            #waterTimes.append(addedTime)
            counter = counter + 1
    while expectedSize < len(waterTimes):
        if(len(waterTimes) - expectedSize == 1):
            waterTimes.pop()
        else:
            waterTimes.pop(0)
            waterTimes.pop()
        count = count + 1
    #print("min * 5: "+str((numMinutesToWater*5)))
    print("len wt x: "+str(len(waterTimes)))
    return waterTimes

#read from settings file and assign variables
with open('testingVariables.txt') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        #if line_count > 1:
        #    continue 
        if line_count == 0:
           print('Column names are '+", ".join(row))
           line_count += 1
           headerRow = row
        elif line_count == 1:
            line_count += 1
            water1 = int(row[0])
            water2 = int(row[1])
            water3 = int(row[2])
            water4 = int(row[3])
            water1segments = int(row[4])
            water2segments = int(row[5])
            water3segments = int(row[6])
            water4segments = int(row[7])
            lighton = int(row[8])
            lightoff = int(row[9])
            tempabove = int(row[10])
            tempbelow = int(row[11])
            humidityabove = int(row[12])
            humiditybelow = int(row[13])
            daystorun = row[14]
            print('\t'+'water1: '+str(water1)+' water2: '+str(water2)+' water3: '+str(water3)+' water4: '+str(water4))
            print('\t'+'lighton: '+str(lighton)+' '+'lightoff: '+str(lightoff))
            print('\t'+'tempabove: '+str(tempabove)+' '+'tempbelow: '+str(tempbelow))
            print('\t'+'humidityabove: '+str(humidityabove)+' '+'humiditybelow: '+str(humiditybelow))
            print('\t'+'daystorun: '+str(daystorun)+'\n\n')
#heater off
os.system("/home/pi/code/codesend 7309745")
#humidifier off
os.system("/home/pi/code/codesend 7309746")
#turn on fan
os.system("/home/pi/code/codesend 7309757")

#set lightsOn
lightsOn = lighton
#set lightsOff
lightsOff = lightoff
#set hoursoflight
hoursoflight = lightoff - lighton


#set now to current time
now = datetime.datetime.now()
#set microseconds to zero for comparision
now = now.replace(microsecond=0)
#set compareTime
compareTime = now
#get and set date
pub_date = datetime.date.today()
#set startofday
startofday = datetime.datetime.combine(pub_date, datetime.time.min)
#if compareTime (current time) is within the light cycle then turn on the grow light
if (compareTime > startofday + datetime.timedelta(hours=lightsOn) and compareTime < startofday + datetime.timedelta(hours=lightsOff)):
    os.system("/home/pi/code/codesend 7309756")
#if compareTime (current time) is outside the light cycle then turn off the grow light
if (compareTime < startofday + datetime.timedelta(hours=lightsOn) or compareTime > startofday + datetime.timedelta(hours=lightsOff)):
    os.system("/home/pi/code/codesend 7309748")

#set up notification interval
lastNotificationTime = datetime.datetime.now() - datetime.timedelta(minutes=5)
message = ""
a = datetime.datetime.now()- datetime.timedelta(minutes=1)

today = datetime.date.today()
wateringTimesPump1 = []

pushInterval = 354
pump1Total = water1
pump1segments = water1segments
pump2Total = water2
pump2segments = water2segments
pump3Total = water3
pump3segments = water3segments
pump4Total = water4
pump4segments = water4segments
wateringTimesPump1 = wateringTimes1minLight(water1, water1segments)
wateringTimesPump2 = wateringTimes1minLight(water2, water2segments)
wateringTimesPump3 = wateringTimes1minLight(water3, water3segments)
wateringTimesPump4 = wateringTimes1minLight(water4, water4segments)
pump1data = 0
pump2data = 0
pump3data = 0
pump4data = 0
heaterOn = False
humidifierOn = False
newDay = False
heaterTime = 0
humidifierTime = 0


while True:
    pub_date = datetime.date.today()
    startofday = datetime.datetime.combine(pub_date, datetime.time.min)
    if(today != pub_date or newDay == True):
        newDay = False
        startofday = datetime.datetime.combine(pub_date, datetime.time.min)
        #print("Minutes to Water Pump1: "+str(pump1Total))
        extraRows = []
        newRow = None
        with open('testingVariables.txt') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print('Column names are '+", ".join(row))
                    line_count += 1
                    headerRow = row
                elif line_count == 1:
                    water1 = int(row[0])
                    water2 = int(row[1])
                    water3 = int(row[2])
                    water4 = int(row[3])
                    water1segments = int(row[4])
                    water2segments = int(row[5])
                    water3segments = int(row[6])
                    water4segments = int(row[7])
                    lighton = int(row[8])
                    lightoff = int(row[9])
                    tempabove = int(row[10])
                    tempbelow = int(row[11])
                    humidityabove = int(row[12])
                    humiditybelow = int(row[13])
                    daystorun = row[14]
                    daystorun = int(daystorun)-1
                    print('\t'+'water1: '+str(water1)+' water2: '+str(water2)+' water3: '+str(water3)+' water4: '+str(water4))
                    print('\t'+'lighton: '+str(lighton)+' '+'lightoff: '+str(lightoff))
                    print('\t'+'tempabove: '+str(tempabove)+' '+'tempbelow: '+str(tempbelow))
                    print('\t'+'humidityabove: '+str(humidityabove)+' '+'humiditybelow: '+str(humiditybelow))
                    print('\t'+'daystorun: '+str(daystorun)+'\n\n')
                    line_count += 1
                    if daystorun != 0:
                        newRow = [str(water1)]+[str(water2)]+[str(water3)]+[str(water4)]+[str(water1segments)]+[str(water2segments)]+[str(water3segments)]+[str(water4segments)]+[str(lighton)]+[str(lightoff)]+[str(tempabove)]+[str(tempbelow)]+[str(humidityabove)]+[str(humiditybelow)]+[str(daystorun)]
                    if daystorun == 0:
                        newDay = True
                else:
                    print("extraRows")
                    extraRows.append(row)
            print('Processed '+str(line_count)+' lines')

        f = open('testingVariables.txt', 'w')

        with f:

            writer = csv.writer(f)
            writer.writerow(headerRow)
            if newRow != None:
                writer.writerow(newRow)
            writer.writerows(extraRows)


        wateringTimesPump1 = wateringTimes1minLight(water1, water1segments)
        wateringTimesPump2 = wateringTimes1minLight(water2, water2segments)
        wateringTimesPump3 = wateringTimes1minLight(water3, water3segments)
        wateringTimesPump4 = wateringTimes1minLight(water4, water4segments)
        today = pub_date

    b = datetime.datetime.now()
    while (b.second != 0) and (b.second%6 != 0):
        time.sleep(.1)
        b = datetime.datetime.now()

    if b.second == 0 or b.second == 30:
        #print("B.SECOND: "+str(b.second))
        ser.reset_input_buffer()
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
            #print(data)
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
            #a = datetime.datetime.now()
            last = 0
            rgb.set_color(PURPLE)
            dt_obj = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
            print(dt_obj)
            point = {
                        "measurement": 'data',
                         "time": dt_obj,
                        "tags": {
                            "section": "section1",
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
        except Exception as e:
            continue
            print(e)


#changed to zero from 59 for testing
    while (b.second != 0) and (b.second%6 != 0):
        #print("Second: "+str(b.second))
        time.sleep(.1)
        b = datetime.datetime.now()
    b = datetime.datetime.now()
    #time.sleep(1)
    now = datetime.datetime.now()
    now = now.replace(microsecond=0)
    compareTime = now
    compareLights = now.replace(second=0, microsecond=0)
    if (b.second == 0 or b.second%6 == 0) and (compareTime >= startofday + datetime.timedelta(hours=lightsOn) and compareTime <= startofday + datetime.timedelta(hours=lightsOff)):
        tempTime = compareTime
        if compareTime in wateringTimesPump1:
            counter1 = 1
            #turn pump on if time in schedule
            pump1.run(Adafruit_MotorHAT.FORWARD)
            #tempTime = compareTime
            if compareTime.second == 0:
                while((tempTime + datetime.timedelta(seconds=6)) in wateringTimesPump1):
                    counter1 = counter1 + 1
                    #print("Counter: "+str(counter))
                    tempTime = tempTime + datetime.timedelta(seconds=6)
                message += "Pump1 on for "+str(counter1*6)+" seconds ("+str(10*counter1)+"ml) at "+str(compareTime)+"\n"
            pump1data += 1
            message += "Pump1: "+str(compareTime)+"\n"
            print("pump 1 watering on")
        else:
            #turn pump off it current time not in schedule
            pump1.run(Adafruit_MotorHAT.RELEASE)

        tempTime = compareTime
        if compareTime in wateringTimesPump2:
            counter2 = 1
            #turn pump on if time in schedule
            pump2.run(Adafruit_MotorHAT.FORWARD)
            #tempTime = compareTime
            if compareTime.second == 0:
                while((tempTime + datetime.timedelta(seconds=6)) in wateringTimesPump2):
                    counter2 = counter2 + 1
                    #print("Counter: "+str(counter2))
                    tempTime = tempTime + datetime.timedelta(seconds=6)
                message += "Pump2 on for "+str(counter2*6)+" seconds ("+str(10*counter2)+"ml) at "+str(compareTime)+"\n"
            pump2data += 1
            message += "Pump2: "+str(compareTime)+"\n"
            print("pump 2 watering on")
        else:
            #turn pump off it current time not in schedule
            pump2.run(Adafruit_MotorHAT.RELEASE)

        tempTime = compareTime
        if compareTime in wateringTimesPump3:
            counter3 = 1
            #turn pump on if time in schedule
            pump3.run(Adafruit_MotorHAT.FORWARD)
            #tempTime = compareTime
            if compareTime.second == 0:
                while((tempTime + datetime.timedelta(seconds=6)) in wateringTimesPump3):
                    counter3 = counter3 + 1
                    #print("Counter: "+str(counter3))
                    tempTime = tempTime + datetime.timedelta(seconds=6)
                message += "Pump3 on for "+str(counter3*6)+" seconds ("+str(10*counter3)+"ml) at "+str(compareTime)+"\n"
            pump3data += 1
            message += "Pump3: "+str(compareTime)+"\n"
            print("pump 3 watering on")
        else:
            #turn pump off it current time not in schedule
            pump3.run(Adafruit_MotorHAT.RELEASE)

        tempTime = compareTime
        if compareTime in wateringTimesPump4:
            counter4 = 1
            #turn pump on if time in schedule
            pump4.run(Adafruit_MotorHAT.FORWARD)
            #tempTime = compareTime
            if compareTime.second == 0:
                while((tempTime + datetime.timedelta(seconds=6)) in wateringTimesPump4):
                    counter4 = counter4 + 1
                    #print("Counter: "+str(counter))
                    tempTime = tempTime + datetime.timedelta(seconds=6)
                message += "Pump4 on for "+str(counter4*6)+" seconds ("+str(10*counter4)+"ml) at "+str(compareTime)+"\n"
            pump4data += 1
            message += "Pump4: "+str(compareTime)+"\n"
            print("pump 4 watering on")
        else:
            #turn pump off it current time not in schedule
            pump4.run(Adafruit_MotorHAT.RELEASE)
        time.sleep(1)
    if (b.second == 30 or b.second == 0) and (compareTime > startofday + datetime.timedelta(hours=lighton) and compareTime < startofday + datetime.timedelta(hours=lightoff)):
        time.sleep(.1)
        tempTarget = round(tempabove + ((tempbelow - tempabove)/2))
        humidityTarget = round(humidityabove + ((humiditybelow - humidityabove)/2))
        if humidity < humidityTarget:
            print("humidifer on humidty is: "+str(humidity)+"+ target is: "+str(humidityTarget))
            os.system("/home/pi/code/codesend 7309754")
            humidifierOn = True
            humidifierTime += 1
        if humidity > humidityTarget:
            print("humidifer off humidty is: "+str(humidity)+"+ target is: "+str(humidityTarget))
            os.system("/home/pi/code/codesend 7309746")
            humidifierOn = False
        if temperature < tempTarget:
            print("heater on temp is: "+str(temperature)+"+ target is: "+str(tempTarget))
            os.system("/home/pi/code/codesend 7309753")
            heaterOn = True
            heaterTime += 1
       if temperature > tempTarget:
            print("heater off temp is: "+str(temperature)+"+ target is: "+str(tempTarget))
            os.system("/home/pi/code/codesend 7309745")
            heaterOn = False
    elif (b.second == 30 or b.second == 0):
        tempTarget = round(tempabove) # + ((tempbelow - tempabove)/2))
        humidityTarget = round(humidityabove) # + ((humiditybelow - humidityabove)/2))
        #if isFieldBelow("humidity", 1, humidityabove):
        if humidity < humidityabove:
            print("humidifer on humidty is: "+str(humidity)+"+ target is: "+str(humidityabove))
            os.system("/home/pi/code/codesend 7309754")
            humidifierOn = True
            humidifierTime += 1
            #message += "Humidifier on at "+str(compareTime)+"\ntarget is "+str(humidityabove)+" it's currently "+str(getLastValue("humidity"))[:4]+"%\n"
        #if isFieldAbove("humidity", 1, humidityabove): #+ ((humiditybelow - humidityabove)/8)):
        if humidity > humidityabove:
            print("humidifer off humidty is: "+str(humidity)+"+ target is: "+str(humidityabove))
            os.system("/home/pi/code/codesend 7309746")
            humidifierOn = False
            #message += "Humidifier off at "+str(compareTime)+"\ntarget is "+str(humidityabove)+" it's currently "+str(getLastValue("humidity"))[:4]+"%\n"
        #if isFieldBelow("temperature", 1, tempabove):
        if temperature < tempabove:
            print("heater on temp is: "+str(temperature)+"+ target is: "+str(tempabove))
            os.system("/home/pi/code/codesend 7309753")
            heaterOn = True
            heaterTime += 1
            #message += "Heater on at "+str(compareTime)+"\ntarget is "+str(tempabove)+" it's currently "+str(getLastValue("temperature"))[:4]+"F\n"
        #if isFieldAbove("temperature", 1, tempabove): #+ ((tempbelow - tempabove)/8)):
        if temperature > tempabove:
            print("heater off temp is: "+str(temperature)+"+ target is: "+str(tempabove))
            os.system("/home/pi/code/codesend 7309745")
            heaterOn = False
            #message += "Heater off at "+str(compareTime)+"\ntarget is "+str(tempabove)+" it's currently "+str(getLastValue("temperature"))[:4]+"F\n"
    #print("compareLights: "+str(compareLights))
    #print("Lights on time: "+str(startofday + datetime.timedelta(hours=lightsOn)))
    #print("Lights off time: "+str(startofday + datetime.timedelta(hours=lightsOff)))
    if(compareLights == startofday + datetime.timedelta(hours=lighton)):
        #if datetime.datetime.now().second == 0:
        message += "Lights on at "+str(compareTime)+" for "+str(hoursoflight)+"hours.\n"
        os.system("/home/pi/code/codesend 7309756")
    if(compareLights == startofday + datetime.timedelta(hours=lightoff)):
        #if datetime.datetime.now().second == 0:
        message += "Lights off at "+str(compareTime)+" for "+str(24-hoursoflight)+"hours.\n"
        os.system("/home/pi/code/codesend 7309748")
    if b.second == 0:
        if humidity < humidityabove:
            #added try except to catch read timeout error
            try:
                if(isFieldBelow("humidity", 20, humidityabove)):
                    sendAlertPushNotification("Humidifier needs to be refilled")
            except:
                print("read timeout")
    if b.second == 0 or b.second == 30:
        try:
            print("writting")
            rgb.set_color(GREEN)
            client.write_points(points, time_precision='ms')
            print("written")
            rgb.set_color(OFF)
        except Exception as e:
            print(e)

    if (((datetime.datetime.now()-a).total_seconds()) >= pushInterval):
        message2 = "Current time: "+str(compareTime)+"\n"
        #message2 += "Current temperature: "+str(getLastValue("temperature"))[:4]+"f\n"
        message2 += "Current temperature: "+str(temperature)[:4]+"f   Target: "+str(tempTarget)+"f\n"
        #message2 += "Current humidity: "+str(getLastValue("humidity"))[:4]+"%\n"
        message2 += "Current humidity: "+str(humidity)[:4]+"%        Target: "+str(humidityTarget)+"%\n"
        message2 += "Over the last 6 minutes...\n"
        message2 += "Heater on for "+str(heaterTime*30)+" seconds\n"
        message2 += "Humidifier on for "+str(humidifierTime*30)+" seconds\n"  
        sendPushNotification(message2+message)
        message = ""
        message2 = ""
        heaterTime = 0
        humidifierTime = 0
        a = datetime.datetime.now()


    #wait for second 1 in current time
    b = datetime.datetime.now()
    while (b.second != 0) and (b.second != 55) and (b.second%6 != 0):

        #print("Second: "+str(b.second))
        time.sleep(.1)
        b = datetime.datetime.now()
#commebted out no seconds printed in output
    #print("Seconds: "+str(b.second))
    if b.second == 55:
        #print("B.SECOND: "+str(b.second))
        points = []
        dt_obj = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        print(dt_obj)
        point = {
                    "measurement": 'water',
                    "time": dt_obj,
                    "tags": {
                        "section": "section1",
                    },
                    "fields": {
                        "pump1": pump1data*10,
                        "pump2": pump2data*10,
                        "pump3": pump3data*10,
                        "pump4": pump4data*10,
                        "date": time.strftime('%d/%m/%Y %H:%M')
                    }
                }
        if(pump1data == 0 and pump2data == 0 and pump3data == 0 and pump4data == 0):
            print("Pumps all zeros")
        else:
            print(point)
            points.append(point)
            print("writting")
            try: 
                client.write_points(points, time_precision='ms')
            except:
                pass
            print("written")
        points = []
        pump1data = 0
        pump2data = 0
        pump3data = 0
        pump4data = 0
