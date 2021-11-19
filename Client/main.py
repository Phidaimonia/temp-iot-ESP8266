from umqtt.robust import MQTTClient
from machine import Pin
import ubinascii
import machine
import ujson as json
import time, ntptime
import onewire, ds18x20
import network
import os
import gc

#import upip
#sys.path.reverse()
#upip.install("micropython-umqtt.simple2")






#######################################################
def measure_temp():
    try:
        ds.convert_temp()
        return round(ds.read_temp(roms[0]), cfg["temp_precision_places"])
    except:
        return -124101.25  #none
    


########################################################
def broadcastData(data):
    client.publish(cfg["mqtt"]["temp_topic"], json.dumps(data), retain=False, qos=0)

###########################################################

def getISOTime():
    t = time.gmtime()
    return "%d-%02d-%02dT%02d:%02d:%09.6f" % (t[0], t[1], t[2], t[3], t[4], t[5])
   
###########################################################






config = open("config.json", "r")
cfg = json.load(config)
config.close()

last_WLAN_state = 0
has_saved_data = False


CLIENT_ID = ubinascii.hexlify(machine.unique_id())
client = MQTTClient(CLIENT_ID, cfg["mqtt"]["broker"], cfg["mqtt"]["port"], cfg["mqtt"]["user"], cfg["mqtt"]["passwd"], keepalive=0, ssl=False)

#client.set_last_will(topic, msg, retain=False, qos=0)
#client.set_callback(on_receive)
# 'Temperature: {}°C'.format(temp)


######################################## Network


wlan = network.WLAN(network.STA_IF)
network.WLAN(network.AP_IF).active(False)


if not wlan.isconnected():
    wlan.active(True)
    wlan.connect(cfg["wifi"]['ssid'],cfg["wifi"]['passwd'])
	
time.sleep(10)

try:
    if wlan.isconnected(): 
        print("Connected to WIFI")
        ntptime.settime()
        client.connect(clean_session=True)
		
    else: print("Not connected to WIFI")

except: 
   print("Can't connect to the broker...") 


######################################### Sensor
ds = ds18x20.DS18X20(onewire.OneWire(Pin(cfg["ds_pin"])))
roms = ds.scan()


#########################################
while True:
    startTime = time.ticks_ms()
    m_temp = measure_temp()
    dataStr = {"team_name": cfg["team"], "created_on":getISOTime(), "temperature": m_temp}
    print(dataStr)   
    
    
    if last_WLAN_state != wlan.status():
        print("WLAN status changed from {} to {}".format(last_WLAN_state, wlan.status()))
        last_WLAN_state = wlan.status()

    if m_temp is not None:
        try:
                if has_saved_data:
                    print("Sending saved data...")
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
            #fileToRead = open("hist.txt", 'r')
            #print("Reading: ", fileToRead.readlines())
            #fileToRead.close()

    print(time.ticks_ms() - startTime)
    time.sleep_ms(cfg["update_period"] * 1000 - time.ticks_ms() + startTime)    