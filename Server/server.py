import tornado
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
from tornado.ioloop import IOLoop
from tornado.web import Application as TornadoApplication
import tornado.web
from urllib.request import urlopen
import datetime as dt, time
import pytz
import tornado.template as T
import json
import paho.mqtt.client as mqtt
import random
import api
import db
from db import DB
import tornado.log
import logging

#Uncomment aftert training# from recognize_handler import RecognizeImageHandler



class RootHandler(tornado.web.RequestHandler):
    def get(self):
        # get username by cookie
        self.write(temp.generate(myvalue="dQw4w9WgXcQ"))        # using templates


class WSHandler(tornado.websocket.WebSocketHandler):
    def initialize(self):
        self.application.ws_clients.append(self)
        app_log.debug("Init WS")

    def open(self):
        self.set_nodelay(True)
        app_log.debug("WebSocket connection opened")

    def on_message(self, message):
        app_log.debug(u"You said: " + message)
        
        try:
            requestData = json.loads(message)           # process requests from frontend
        except:
            app_log.error("Bad request " + message)
            self.write_message("Bad request")
            return

        if "request_type" not in requestData:
            app_log.error("Request type missing " + message)
            self.write_message("request_type missing")
            return

        if requestData["request_type"] == "temperature_data":                           # get temperatures from->to
            if db_connected:
                if ("dt_from" in requestData) and ("dt_to" in requestData) and ("cookie" in requestData):
                
                    dt_from = pytz.utc.localize(dt.datetime.fromisoformat(requestData["dt_from"]))              # all time operations in UTC
                    dt_to = pytz.utc.localize(dt.datetime.fromisoformat(requestData["dt_to"]))

                    data = database.read_messages(dt_from, dt_to, team_list)        # returns json
                    for measurement in data:
                        self.write_message(measurement)
                else:
                    app_log.error("Bad request parameters " + message)
                    self.write_message("Bad Bad request parameters")
                    return
            else:
                self.write_message("Error: DB not connected...")


        elif requestData["request_type"] == "sensor_status":                            # last online time
            for t_team in sensor_status:
                response = {"response_type":"sensor_status", "team_name":t_team, "last_seen":sensor_status[t_team]}
                self.write_message(json.dumps(response))


        elif requestData["request_type"] == "aimtec_status":                            

            response = {"response_type":"aimtec_status", "status":aimtec.is_online()}                   # aimtec
            self.write_message(json.dumps(response))
  
        else:
            app_log.error("Bad request type " + message)
            self.write_message("Bad request_type")
            return

    
            

    def on_close(self):
        self.application.ws_clients.remove(self)
        app_log.debug("WebSocket closed")



def on_connect_MQTT(client, userdata, flags, rc):
    app_log.debug("Connected with result code "+str(rc))

    client.subscribe(cfg["mqtt"]["room_name"] + "/" + cfg["mqtt"]["listen_topic"])


def on_message_MQTT(client, userdata, msg):
    msg_str = msg.payload.decode('utf-8')

    app_log.debug(msg.topic+" "+msg_str)
    
    try:
        data = json.loads(msg_str)
    except:
        app_log.debug("E: Error when parsing message")
        return

    if ("team_name" in data) and ("created_on" in data) and ("temperature" in data):                    # valid json
        if not data["team_name"] == msg.topic.replace(mqtt_room_name + "/", ""):                        # topic == team
            app_log.debug("E: Team name '{}' and topic '{}' don't match.".format(data["team_name"], msg.topic))
            return

        if data["team_name"] not in team_list:                                                          # team in teamlist
            app_log.error("E: Team name '{}' is not on the team list.".format(data["team_name"]))
            return

        try:
            temp = float(data["temperature"])                                                           # temperature is float
        except Exception as err:   
            app_log.error("E: Can't parse temperature {}".format(data["temperature"]))
            app_log.error(str(err))
            return

        try:
            data["created_on"] = pytz.utc.localize(db.fuzzy_ISO_to_datetime(data["created_on"])).isoformat()         # correct isoformat
        except Exception as err:   # ValueError
            app_log.error("E: Can't parse time {}".format(data["created_on"]))
            app_log.error(str(err))
            return

        final_msg = json.dumps(data)
        
        #print("Final datapoint: " + final_msg)
        if db_connected:
            app_log.debug(database.write_message(msg_str))                # save to db

        sensor_status[data["team_name"]] = time.gmtime()          # last online = now
        app.send_ws_message(final_msg)                            # push to frontend

        #if aimtec_connected and data["team_name"] == cfg["team"]:   # send our team's data to Aimtec
            #aimtec.write_message(msg_str)
            #if(data["temperature"] > aimtec.sensor.max_temperature or data["temperature"] < aimtec.sensor.min_temperature):
            #    app_log.debug("ALERT SENT: " + msg_str + " " + str(aimtec.send_alert(msg_str)))
        

    


class ReceiveImageHandler(tornado.web.RequestHandler):
    def post(self):
        # Convert from binary data to string
        received_data = self.request.body.decode()

        assert received_data.startswith("data:image/png"), "Only data:image/png URL supported"

        # Parse data:// URL
        with urlopen(received_data) as response:
            image_data = response.read()

        app_log.info("Received image: %d bytes", len(image_data))

        # Write an image to the file
        with open('faceid/images/img-{}.png'.format(dt.datetime.now().strftime('%Y%m%d-%H%M%S')), "wb") as fw:
            fw.write(image_data)




class WebApp(TornadoApplication):

    def __init__(self):
        self.ws_clients = []

        self.tornado_handlers = [
            (r'/', RootHandler),
            (r"/receive_image", ReceiveImageHandler),
            #Uncomment after training# (r"/recognize", RecognizeImageHandler),
            (r'/data', WSHandler),
            (r'/(.*)', tornado.web.StaticFileHandler, {'path': './static'})
        ]
        self.tornado_settings = {
            "debug": True,
            "autoreload": True
        }
        TornadoApplication.__init__(self, self.tornado_handlers, **self.tornado_settings)

    def send_ws_message(self, message):
        for client in self.ws_clients:
            iol.spawn_callback(client.write_message, message)




if __name__ == '__main__':
    
    config = open("config.json", "r")   # load parameters
    cfg = json.load(config)
    config.close()

    tornado.log.enable_pretty_logging()
    app_log = logging.getLogger("tornado.application")
    app_log.setLevel(logging.DEBUG)
    mqtt_client_id = "observer" + str(random.randint(10000000, 999999999999))
    mqtt_room_name = cfg["mqtt"]["room_name"]

    team_list = ["red", "blue", "black", "pink", "green"]
    sensor_status = {name:None for name in team_list}

    loader = T.Loader("./static/")
    temp = loader.load("index.html")


    aimtec = None
    aimtec_connected = False
    for i in range(cfg["reconnect_tries"]):  
        try:
            aimtec = api.Api(cfg["aimtec"]["user"], cfg["aimtec"]["passwd"])
            if aimtec is not None:
                if aimtec.connected:
                    aimtec_connected = True
                    break
        except Exception as err:
            app_log.error("Aimtec connection error: {}".format(err))
            app_log.error("Connection attempt {}...".format(i+1))
            time.sleep(cfg["reconnect_timeout"])

    db_connected = False
    database = None
    app_log.debug("Connecting to DB...")
    for i in range(cfg["reconnect_tries"]):  
        try:
            app_log.debug("Connection attempt {}...".format(i+1))
            database = DB()
            if database is not None:
                if database.connected == True:
                    db_connected = True
                    break
        except Exception as err:
            app_log.error("Database connection error: {}".format(err))
            time.sleep(2)       # cfg["reconnect_timeout"]


    if not db_connected:
        app_log.error("Can't connect to DB, continuing...")
    else:
        app_log.debug("Connected to DB")


    client = mqtt.Client(mqtt_client_id)
    client.username_pw_set(cfg["mqtt"]["user"], cfg["mqtt"]["passwd"])


    client.on_connect = on_connect_MQTT
    client.on_message = on_message_MQTT

    try:
        client.connect(cfg["mqtt"]["broker"], cfg["mqtt"]["port"])
        client.loop_start()
    except Exception:
        app_log.critical("Can't connect to MQTT broker")
        pass

    app = WebApp()
    
    
    ssl_options={
        "certfile": "./letsencrypt/cert.pem",
        "keyfile": "./letsencrypt/key.pem",
        "ca_certs": "./letsencrypt/fullchain.pem",
    }

    http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_options)    # ssl_options=ssl_options
    http_server.listen(443)

    iol = IOLoop.current()
    print('Webserver: Initialized...')
    iol.start()




