import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.template as T
import json
import paho.mqtt.client as mqtt

CLIENT_ID = "broker_RED_team_346573"

class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(temp.generate(myvalue="dQw4w9WgXcQ"))


class JSONHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(json.dumps(slovnik))


def on_connect_MQTT(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe(cfg["mqtt"]["listen_topic"])


def on_message_MQTT(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))




config = open("config.json", "r")   # load parameters
cfg = json.load(config)
config.close()


client = mqtt.Client(CLIENT_ID)
client.username_pw_set(cfg["mqtt"]["user"], cfg["mqtt"]["passwd"])


client.on_connect = on_connect_MQTT
client.on_message = on_message_MQTT

client.connect(cfg["mqtt"]["broker"], cfg["mqtt"]["port"])



application = tornado.web.Application(handlers=[
    (r'/', RootHandler),
    (r'/json/', JSONHandler),
    (r'/json', JSONHandler),
    ('/(.*)', tornado.web.StaticFileHandler, {'path': './static'})

])

if __name__ == '__main__':
    
    loader = T.Loader("./Static/HTML/")
    temp = loader.load("index.html")

    slovnik = {"HTTP" : 80, 
                "HTTPS" : 443}


    http_server = tornado.httpserver.HTTPServer(application)

    # ssl_options={
    #    "certfile": "./letsencrypt/cert.pem",
    #    "keyfile": "./letsencrypt/key.pem",
    #    "ca_certs": "./letsencrypt/fullchain.pem",
    #}


    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()


