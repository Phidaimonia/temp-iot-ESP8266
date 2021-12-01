import tornado.httpserver
import tornado.websocket
import tornado.ioloop
from tornado.web import Application as TornadoApplication
import tornado.web
import tornado.template as T
import json
import paho.mqtt.client as mqtt
from tornado.ioloop import IOLoop

CLIENT_ID = "RED_team_3213"

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
        self.application.ws_clients.remove(self)
        print("WebSocket closed")

    def initialize(self):
        self.application.ws_clients.append(self)
        print('Init WS')






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

    config = open("config.json", "r")   # load parameters
    cfg = json.load(config)
    config.close()
    

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


    ######################################################
    """
    httpApp = tornado.web.Application(handlers=[
        (r'/', RootHandler),
        (r'/json/', JSONHandler),
        (r'/colors', colorWSHandler),
        ('/(.*)', tornado.web.StaticFileHandler, {'path': './static'})

    ])
    """


    app = WebApp()
    app.listen(80)

    iol = IOLoop.current()
    print('Webserver: Initialized. Listening on 80')
    iol.start()




