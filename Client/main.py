import time
#print("15 sec until main starts")
#time.sleep(15)
print("Started now")

startTime = time.ticks_ms()


from umqtt.simple import MQTTClient
from machine import Pin
import ubinascii
import machine
import ujson as json
import ntptime
import onewire, ds18x20
import network
import os


#######################################################
def measure_temp():
    try:
        ds.convert_temp()
        return round(ds.read_temp(roms[0]), cfg["temp_precision_places"])
    except:
        raise 1


def save_data(data):
    try:
        with open(historyFileName, "a") as temp_history:
            temp_history.write(json.dumps(data))
            temp_history.write('\n')
            temp_history.close()
    except Exception:
        print("Can't save data, not enough memory?")


def get_last_checkpoint():
    try:
        with open(variablesFileName, 'r') as f:
            tm = f.readline()
            f.close()
        return int(tm)
    except Exception:
        return time.time() + cfg["update_period"] - (time.time() + cfg["update_period"]) % cfg["update_period"]


def set_next_checkpoint(tm):
    try:
        with open(variablesFileName, 'w') as f:
            f.write(str(tm))   
            f.close()
    except Exception:
        print("Can't set next checkpoint, not enough memory?")

    


########################################################
def broadcastData(data):
    try:
        client.publish(cfg["mqtt"]["temp_topic"] + cfg["team"], json.dumps(data), retain=False, qos=1)
    except Exception as err:
        raise 2 

###########################################################

def getISOTime():
    t = time.gmtime()
    return "%d-%02d-%02dT%02d:%02d:%09.6f" % (t[0], t[1], t[2], t[3], t[4], t[5])
   
###########################################################

# STATUS: 0 - no connection, 1 - connected to WIFI
status = 0
variablesFileName = "vars.txt"
historyFileName = "hist.txt"

config = open("config.json", "r")
cfg = json.load(config)
config.close()

CLIENT_ID = ubinascii.hexlify(machine.unique_id())
client = MQTTClient(CLIENT_ID, cfg["mqtt"]["broker"], cfg["mqtt"]["port"], cfg["mqtt"]["user"], cfg["mqtt"]["passwd"], keepalive=0, ssl=False)

######################################## Network

wlan = network.WLAN(network.STA_IF)
network.WLAN(network.AP_IF).active(False)

wlan.active(True)
wlan.connect(cfg["wifi"]['ssid'],cfg["wifi"]['passwd'])

while wlan.status() == network.STAT_CONNECTING:
    machine.idle()

print("WIFI status: {}".format(wlan.status()))

if wlan.isconnected():
    try:
        ntptime.settime()
        client.connect(clean_session=False)
        status = 1
    except Exception as err: 
        print("WIFI connected but can't reach MQTT broker or NTP server") 
        print("Exception number: {}".format(err)) 
        status = 0
else:
    print("NOT connected to WIFI")


######################################### Sensor
ds = ds18x20.DS18X20(onewire.OneWire(Pin(cfg["ds_pin"])))
roms = ds.scan()

#########################################


next_stop = get_last_checkpoint() + cfg["update_period"]
next_stop = min(next_stop, time.time(), time.time() + cfg["update_period"] - (time.time() + cfg["update_period"]) % cfg["update_period"])

set_next_checkpoint(next_stop)


m_temp = measure_temp()
dataDict = {"team_name": cfg["team"], "created_on":getISOTime(), "temperature": m_temp}

#save_data(dataDict)

if m_temp is not None:
    if status == 1:     # connected to broker
        try:    
            broadcastData(dataDict)
            try:
                with open(historyFileName, 'r') as dataFile:
                    savedCounter = 0
                    print("Sending saved data...")

                    for line in dataFile:
                        line = line.replace("'", "\"")
                        broadcastData(json.loads(line))
                        savedCounter += 1

                    dataFile.close()
                    print("     There\'s {} lines saved".format(savedCounter))
                            
                    os.remove(historyFileName)
            except Exception:
                pass    # file doesn't exist -> no data to send

        except Exception as err: 
            print("Exception number: {}".format(err))
            print("Can't send data, saving for later...") 
            save_data(dataDict)

    else: 
        save_data(dataDict)
else:
    if status == 1:  
        broadcastData({"team_name": cfg["team"], "created_on":getISOTime(), "message": "Sensor is broken..."})



#print("Now is {}".format(time.time()))
#print("Next stop is {}".format(next_stop))
waitTime = max(next_stop - time.time(), 1)
#print("Wait time is {}".format(waitTime))

print("It took {} seconds".format((time.ticks_ms() - startTime) / 1000.0))
