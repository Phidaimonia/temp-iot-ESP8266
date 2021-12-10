import machine, os, ubinascii, ntptime, network, onewire, ds18x20, time
from umqtt.simple import MQTTClient
from machine import Pin, RTC, Timer
import ujson as json

print("Reboot...")


def measure_temp_median():
    try:
        x = [0.0, 0.0, 0.0]
        for i in range(3):
            ds.convert_temp()
            x[i] = round(ds.read_temp(roms[0]), cfg["temp_precision_places"])
            machine.lightsleep(100)

        min_x = min(min(x[0], x[1]), x[2])
        max_x = max(max(x[0], x[1]), x[2])

        return x[0] + x[1] + x[2] - min_x - max_x # median
    except:
        return None


def save_data(data):
    try:
        with open(historyFileName, "a") as temp_history:
            temp_history.write(data + "\n")
    except Exception:
        os.remove(historyFileName)
        print("Can't save data, not enough memory?")


def file_exists(fname):
    try:
        with open(fname, 'r') as f:
            return True
    except Exception:
        return False


def broadcastData(data):
    try:
        client.publish(cfg["mqtt"]["temp_topic"] + cfg["team"], data, retain=False, qos=1)
    except Exception as err:
        raise err


def getISOTime():
    t = time.gmtime()
    return "%d-%02d-%02dT%02d:%02d:%09.6f" % (t[0], t[1], t[2], t[3], t[4], t[5])
   
justBooted = True
historyFileName = "hist.txt"

config = open("config.json", "r")
cfg = json.load(config)
config.close()

CLIENT_ID = ubinascii.hexlify(machine.unique_id())
client = MQTTClient(CLIENT_ID, cfg["mqtt"]["broker"], cfg["mqtt"]["port"], cfg["mqtt"]["user"], cfg["mqtt"]["passwd"], keepalive=0, ssl=False)

wlan = network.WLAN(network.STA_IF)
network.WLAN(network.AP_IF).active(False)

ds = ds18x20.DS18X20(onewire.OneWire(Pin(cfg["ds_pin"])))
roms = ds.scan()

m_temp = measure_temp_median()  # first measure to init sensor properly

while 1:
    startTime = time.ticks_ms()
    connected = False

    if not wlan.isconnected():
        wlan.active(True)
        wlan.connect(cfg["wifi"]['ssid'],cfg["wifi"]['passwd'])

    timer = Timer(-1)
    timer.init(period=cfg["wifi_connection_timeout"] * 1000, mode=Timer.ONE_SHOT, callback=lambda t: wlan.active(False))

    while (wlan.status() == network.STAT_CONNECTING):
        machine.idle()

    timer.deinit()

    if wlan.isconnected():
        try:
            ntptime.settime()
            connected = True
            #print("Synchronized...")
        except Exception as err: 
            print("Can't reach NTP server") 
            print("Exception number: {}".format(err)) 
            connected = False
    else:
        print("NOT connected to WIFI")

    if connected:
        try:
            client.connect(clean_session=False)
            connected = True
            #print("Connected to broker")
        except Exception as err: 
            print("Can't reach MQTT broker") 
            print("Exception number: {}".format(err)) 
            connected = False


    if (not connected) and justBooted:   
        if file_exists(historyFileName):
            os.remove(historyFileName)   

    #if connected and file_exists(historyFileName): 
        #adjustDatetime

    m_temp = measure_temp_median()
    dataStr = json.dumps({"team_name": cfg["team"], "created_on":getISOTime(), "temperature": m_temp})

    if not justBooted:
        if m_temp is not None:
            if connected: 
                    try:
                        with open(historyFileName, 'r') as dataFile:
                            print("     Sending saved data...")
                            validData = True

                            for line in dataFile:
                                broadcastData(line.replace("\n", ""))

                            dataFile.close()
                            os.remove(historyFileName)
                        broadcastData(dataStr)
                    except OSError as err:
                        print("No saved data to send...") 
                        broadcastData(dataStr)
                    except umqtt.MQTTException as err: 
                        print("Exception number: {}".format(err))
                        print("Can't send data, saving for later...") 
                        save_data(dataStr)
            else: 
                save_data(dataStr)
        else:
            if connected:  
                broadcastData({"team_name": cfg["team"], "created_on":getISOTime(), "message": "Sensor is broken..."})


    if justBooted:
        next_stop = time.time() + cfg["update_period"] - time.time() % cfg["update_period"]
    next_stop = min(next_stop + cfg["update_period"], time.time() + cfg["update_period"] - time.time() % cfg["update_period"])
    waitTime = max(next_stop - time.time(), 10)

    print("Wait time is {}".format(waitTime))
    print("It took {} seconds".format((time.ticks_ms() - startTime) / 1000.0))
    justBooted = False

    if not connected:
        wlan.active(False)

    machine.lightsleep(waitTime * 1000)
