import tornado.httpserver
import tornado.websocket
import tornado.ioloop
from tornado.web import Application as TornadoApplication
import tornado.web
import tornado.template as T
import json
import paho.mqtt.client as mqtt
from tornado.ioloop import IOLoop

CLIENT_ID = "broker_RED_team_346573"

class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(temp.generate(myvalue="dQw4w9WgXcQ"))


class JSONHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(json.dumps(slovnik))


class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket connection opened")

    def on_message(self, message):
        print(u"You said: " + message)

    def on_close(self):
        print("WebSocket closed")

    def initialize(self):
        self.application.ws_clients.append(self)
        print('Init WS')






def on_connect_MQTT(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe(cfg["mqtt"]["listen_topic"])


def on_message_MQTT(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    app.send_ws_message(msg.topic+" "+str(msg.payload))

    #write_message(str(msg.payload))





class WebWSApp(TornadoApplication):

    def __init__(self):
        self.ws_clients = []

        self.tornado_handlers = [
            (r'/', RootHandler),
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
    
    loader = T.Loader("./Static/HTML/")
    temp = loader.load("index.html")

    slovnik = {"item 1" : 123, 
                "item 2" : 277}
    

    # ssl_options={
    #    "certfile": "./letsencrypt/cert.pem",
    #    "keyfile": "./letsencrypt/key.pem",
    #    "ca_certs": "./letsencrypt/fullchain.pem",
    #}


    
    config = open("config.json", "r")   # load parameters
    cfg = json.load(config)
    config.close()


    client = mqtt.Client(CLIENT_ID)
    client.username_pw_set(cfg["mqtt"]["user"], cfg["mqtt"]["passwd"])


    client.on_connect = on_connect_MQTT
    client.on_message = on_message_MQTT

    client.connect(cfg["mqtt"]["broker"], cfg["mqtt"]["port"])

    client.loop_start()


    ######################################################
    """
    httpApp = tornado.web.Application(handlers=[
        (r'/', RootHandler),
        (r'/json/', JSONHandler),
        (r'/colors', colorWSHandler),
        ('/(.*)', tornado.web.StaticFileHandler, {'path': './static'})

    ])
    """


    app = WebWSApp()
    app.listen(80)

    iol = IOLoop.current()
    iol.start()

    print('Webserver: Initialized. Listening on 80')


