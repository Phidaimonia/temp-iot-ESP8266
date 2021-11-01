from umqtt.simple import MQTTClient
from machine import Pin
import ubinascii
import machine
import ujson as json
import time, ntptime
import onewire, ds18x20
import network
import os
import gc




#######################################################
def measure_temp():
    try:
        ds.convert_temp()
        return round(ds.read_temp(roms[0]), 2)
    except:
        return cfg['min_temp'] - 1.0
    


########################################################
def broadcastData(data):
    print(data)     # 'Temperature: {}°C'.format(temp)
    client.publish(cfg["mqtt"]["temp_topic"], json.dumps(data))

###########################################################






config = open("config.json", "r")
cfg = json.load(config)
config.close()

last_WLAN_state = 0
has_saved_data = False


CLIENT_ID = ubinascii.hexlify(machine.unique_id())
client = MQTTClient(CLIENT_ID, cfg["mqtt"]["broker"], cfg["mqtt"]["port"], cfg["mqtt"]["user"], cfg["mqtt"]["passwd"])


######################################## Network


wlan = network.WLAN(network.STA_IF)
network.WLAN(network.AP_IF).active(False)


if not wlan.isconnected():
    wlan.active(True)
    wlan.connect(cfg["wifi"]['ssid'],cfg["wifi"]['passwd'])

try:
    if wlan.isconnected(): 
        print("Connected to WIFI")
        #ntptime.settime()
        #client.connect()
    else: print("Not connected to WIFI")

except: 
   print("Can't connect to the broker...") 


######################################### Sensor
ds = ds18x20.DS18X20(onewire.OneWire(Pin(cfg["ds_pin"])))
roms = ds.scan()



#########################################
while True:
    dataStr = {"temperature": measure_temp(), "time": time.time()}

    if last_WLAN_state != wlan.status():
        print("WLAN status changed from {} to {}".format(last_WLAN_state, wlan.status()))
        last_WLAN_state = wlan.status()

    try:
        if has_saved_data:
          
            dataFile = open("hist.txt", 'r')
            data = dataFile.readlines()
            dataFile.close()

            for line in data:
                broadcastData(line)
			
			broadcastData(dataStr)
            
            os.remove("hist.txt")
			has_saved_data = False
            gc.collect()

        else:
            broadcastData(dataStr)
    except: 
        print("Can't send data, saving for later...") 
        temp_history = open("hist.txt", "a")
        temp_history.write(json.dumps(dataStr))
        temp_history.write('\n')
        temp_history.close()

        has_saved_data = True

		###
        fileToRead = open("hist.txt", 'r')
        print("Reading: ", fileToRead.readlines())
        fileToRead.close()


    time.sleep(cfg["update_period"])




