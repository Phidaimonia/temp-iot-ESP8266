import tornado.httpserver
import tornado.websocket
import tornado.ioloop
from tornado.ioloop import IOLoop
from tornado.web import Application as TornadoApplication
import tornado.web
from urllib.request import urlopen
import datetime as dt
import tornado.template as T
import json
import paho.mqtt.client as mqtt
import random
from db import DB


#Uncomment aftert training# from recognize_handler import RecognizeImageHandler

import tornado.log
import logging

tornado.log.enable_pretty_logging()
app_log = logging.getLogger("tornado.application")
CLIENT_ID = "RED_team_" + str(random.randint(10000000, 999999999999))




class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(temp.generate(myvalue="dQw4w9WgXcQ"))


class JSONHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(json.dumps(slovnik))


class WSHandler(tornado.websocket.WebSocketHandler):
    def initialize(self):
        self.application.ws_clients.append(self)
        app_log.debug("Init WS")
        print('Init WS')

    def open(self):
        self.set_nodelay(True)
        print("WebSocket connection opened")

    def on_message(self, message):
        print(u"You said: " + message)

    def on_close(self):
        self.application.ws_clients.remove(self)
        print("WebSocket closed")



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
        with open(f"images/img-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.png", "wb") as fw:
            fw.write(image_data)



def on_connect_MQTT(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe(cfg["mqtt"]["listen_topic"])


def on_message_MQTT(client, userdata, msg):
    msg_str = msg.payload.decode('utf-8')
    print(msg.topic+" "+msg_str)
    try:
        message = json.loads(msg_str)
    except:
        print("E: Error when parsing message")
        return
    if not message["team_name"] == msg.topic[4:]:
        print("E: Team name '{}' and topic '{}' don't match.".format(message["team_name"], msg.topic))
        return

    app.send_ws_message(msg_str)

    #write_message(msg_str)





class WebApp(TornadoApplication):

    def __init__(self):
        self.ws_clients = []

        self.tornado_handlers = [
            (r'/', RootHandler),
            (r"/receive_image", ReceiveImageHandler),
            #Uncomment aftert training# (r"/recognize", RecognizeImageHandler),
            (r'/json/', JSONHandler),
            (r'/data', WSHandler),
            ('/(.*)', tornado.web.StaticFileHandler, {'path': './static'})
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
    
    loader = T.Loader("./Static/")
    temp = loader.load("index.html")

    slovnik = {"item 1" : 123, 
                "item 2" : 277}

    config = open("config.json", "r")   # load parameters
    cfg = json.load(config)
    config.close()

    database = DB()
    

    # ssl_options={
    #    "certfile": "./letsencrypt/cert.pem",
    #    "keyfile": "./letsencrypt/key.pem",
    #    "ca_certs": "./letsencrypt/fullchain.pem",
    #}




    client = mqtt.Client(CLIENT_ID)
    client.username_pw_set(cfg["mqtt"]["user"], cfg["mqtt"]["passwd"])


    client.on_connect = on_connect_MQTT
    client.on_message = on_message_MQTT

    client.connect(cfg["mqtt"]["broker"], cfg["mqtt"]["port"])
    client.loop_start()

    app = WebApp()
    app.listen(80)

    iol = IOLoop.current()
    print('Webserver: Initialized. Listening on 80')
    iol.start()




