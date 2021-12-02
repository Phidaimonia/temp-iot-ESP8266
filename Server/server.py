import tornado
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
from tornado.ioloop import IOLoop
from tornado.web import Application as TornadoApplication
import tornado.web
from urllib.request import urlopen
import datetime as dt
import pytz
import tornado.template as T
import json
import paho.mqtt.client as mqtt
import random
import api
from db import DB
import tornado.log
import logging

#Uncomment aftert training# from recognize_handler import RecognizeImageHandler



class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(temp.generate(myvalue="dQw4w9WgXcQ"))


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
            requestData = json.loads(message)
        except:
            app_log.debug("Bad request... " + message)
            self.write_message("Bad request")
            return
        if ("dt_from" in requestData) and ("dt_to" in requestData) and ("cookie" in requestData):
            dt_from = pytz.utc.localize(dt.datetime.fromisoformat(requestData["dt_from"]))
            dt_to = pytz.utc.localize(dt.datetime.fromisoformat(requestData["dt_to"]))

            data = database.read_messages(dt_from, dt_to, team_list)
            for measurement in data:
                self.write_message(measurement)

    def on_close(self):
        self.application.ws_clients.remove(self)
        app_log.debug("WebSocket closed")



def on_connect_MQTT(client, userdata, flags, rc):
    app_log.debug("Connected with result code "+str(rc))

    client.subscribe(cfg["mqtt"]["room_name"] + "/" + cfg["mqtt"]["listen_topic"])


def on_message_MQTT(client, userdata, msg):
    msg_str = msg.payload.decode('utf-8')

    print(msg.topic+" "+msg_str)
    
    try:
        data = json.loads(msg_str)
    except:
        app_log.debug("E: Error when parsing message")
        return
    if ("team_name" in data) and ("created_on" in data) and ("temperature" in data):
        if not data["team_name"] == msg.topic.replace(mqtt_room_name, ""):
            print("E: Team name '{}' and topic '{}' don't match.".format(data["team_name"], msg.topic))
            return
        if data["team_name"] not in team_list:
            print("E: Team name '{}' is not on the team list.".format(data["team_name"]))
            return
        
        print(database.write_message(msg_str))
        app.send_ws_message(msg_str)
        

    


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
        with open('images/img-{}.png'.format(dt.datetime.now().strftime('%Y%m%d-%H%M%S')), "wb") as fw:
            fw.write(image_data)




class WebApp(TornadoApplication):

    def __init__(self):
        self.ws_clients = []

        self.tornado_handlers = [
            (r'/', RootHandler),
            (r"/receive_image", ReceiveImageHandler),
            #Uncomment aftert training# (r"/recognize", RecognizeImageHandler),
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
    mqtt_client_id = "observer" + str(random.randint(10000000, 999999999999))
    mqtt_room_name = cfg["mqtt"]["room_name"]

    team_list = ["red", "blue", "black", "pink", "green"]

    
    loader = T.Loader("./static/")
    temp = loader.load("index.html")


    aimtec = api.Api(cfg["aimtec"]["user"], cfg["aimtec"]["user"])
    aimtec.write_message('{"team_name": "white", "created_on": "2021-11-27T12:25:05.336974", "temperature": 25.72}')


    
    try:
        database = DB()
    except Exception as err:
        raise err



    client = mqtt.Client(mqtt_client_id)
    client.username_pw_set(cfg["mqtt"]["user"], cfg["mqtt"]["passwd"])


    client.on_connect = on_connect_MQTT
    client.on_message = on_message_MQTT

    client.connect(cfg["mqtt"]["broker"], cfg["mqtt"]["port"])
    client.loop_start()

    app = WebApp()
    

    ssl_options={
        "certfile": "./letsencrypt/cert.pem",
        "keyfile": "./letsencrypt/key.pem",
        "ca_certs": "./letsencrypt/fullchain.pem",
    }

    http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_options)
    http_server.listen(443)

    iol = IOLoop.current()
    print('Webserver: Initialized...')
    iol.start()




