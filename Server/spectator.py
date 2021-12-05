
import json
import paho.mqtt.client as mqtt
import random


CLIENT_ID = "RED_team_" + str(random.randint(10000000, 999999999999))


def on_connect_MQTT(client, userdata, flags, rc):
    client.subscribe(cfg["mqtt"]["room_name"] + "/" + cfg["mqtt"]["listen_topic"])


def on_message_MQTT(client, userdata, msg):
    msg_str = msg.payload.decode('utf-8')
    print(msg_str)  #msg.topic+" "+
    

    




if __name__ == '__main__':
    
    config = open("config.json", "r")   # load parameters
    cfg = json.load(config)
    config.close()

    client = mqtt.Client(CLIENT_ID)
    client.username_pw_set(cfg["mqtt"]["user"], cfg["mqtt"]["passwd"])


    client.on_connect = on_connect_MQTT
    client.on_message = on_message_MQTT

    client.connect(cfg["mqtt"]["broker"], cfg["mqtt"]["port"])
    client.loop_start()



    input("")



