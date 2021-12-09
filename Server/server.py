import tornado
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from tornado.ioloop import IOLoop
from tornado.web import Application as TornadoApplication
import tornado.template as T

import api, db
from db import DB

from urllib.request import urlopen
import datetime as dt, time, pytz
from datetime import timezone

import json
import paho.mqtt.client as mqtt
import random
import logging, tornado.log

import utils

test_mode = False  # disable SSL


from recognize_handler import RecognizeImageHandler


class UserHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_id = self.get_secure_cookie("session")
        if user_id is None: return None  # or not db_connected: return None

        return database.getUser(int(user_id.decode("utf-8")))

class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie("session")
        self.render("Static/index.html")

class RootHandler(tornado.web.RequestHandler):
    async def get(self):
        self.render("Static/index.html")


class WSHandler(tornado.websocket.WebSocketHandler):
    def get_current_user(self):
        user_id = self.get_secure_cookie("session")
        if user_id is None: return None  # or not db_connected: return None

        return database.getUser(int(user_id.decode("utf-8")))

    def initialize(self):
        self.application.ws_clients.append(self)
        app_log.debug("Init WS")

    def open(self):
        self.set_nodelay(True)
        #if db_connected:
        if not self.current_user:
            self.try_send_message("Not logged in, good bye")
            app_log.error("Not logged in, closing WS")
            self.close()
            return
        app_log.debug("WebSocket connection opened")

    def try_send_message(self, content):
        try:
            self.write_message(content)
        except Exception as err:
            app_log.error("E: WS error: Can't send data")
            app_log.error(str(err))
            app.ws_clients.remove(self)
            self.close()


    async def on_message(self, message):
        app_log.debug(u"You said: " + message)
        
        try:
            requestData = json.loads(message)           # process requests from frontend
        except:
            app_log.error("Bad request " + message)
            self.try_send_message({"error" : "Bad request"})
            return

        if "request_type" not in requestData:
            app_log.error("Request type missing " + message)
            self.try_send_message({"error" : "request_type missing"})
            return
            

        if requestData["request_type"] == "temperature_data":                           # get temperatures from->to
            if ("dt_from" in requestData) and ("dt_to" in requestData) and ("interval" in requestData):
                
                try:
                    dt_from = utils.fuzzy_ISO_to_datetime(requestData["dt_from"])              # all time operations in naive UTC
                    dt_to = utils.fuzzy_ISO_to_datetime(requestData["dt_to"])
                except Exception as err:
                    app_log.error("Bad time format " + message)
                    app_log.error(str(err))
                    self.try_send_message({"error" : "Bad request"})
                    return

                data = database.read_min_max_messages(dt_from, dt_to, team_list, dt.timedelta(minutes=requestData["interval"]))        # returns json
                for measurement in data:
                    measurement["created_on"] = utils.fix_isoformat(measurement["created_on"])
                    measurement["response_type"] = "temperature_data"
                    self.try_send_message(measurement)
            else:
                app_log.error("Bad request parameters " + message)
                self.try_send_message({"error" : "Bad request parameters"})
                return

            #if db_connected:
            #    self.try_send_message({"error" : "DB not connected"})


        elif requestData["request_type"] == "sensor_status":                            # last online time
            for t_team in team_list:
                response = {"response_type":"sensor_status", "team_name":t_team, "last_seen":sensor_status[t_team]}
                app_log.debug(response)
        
                self.try_send_message(json.dumps(response))


        elif requestData["request_type"] == "aimtec_status":                            
            response = {"response_type":"aimtec_status", "status":await aimtec.is_online()}                   # aimtec
            self.try_send_message(json.dumps(response))

        elif requestData["request_type"] == "get_username":                            
            usr = self.get_current_user()
            if usr is None:
                response = {"response_type":"get_username", "username":"Guest"} 
            else: 
                response = {"response_type":"get_username", "username":usr.username}              
            self.try_send_message(json.dumps(response))
  
        else:
            app_log.error("Bad request type " + message)
            self.try_send_message({"error" : "Bad request_type"})
            return

    def on_close(self):
        self.application.ws_clients.remove(self)
        app_log.debug("WebSocket closed")




class StaticUserHandler(UserHandler, tornado.web.StaticFileHandler):
    @tornado.web.authenticated
    def prepare(self):
        pass

class LoginHandler(UserHandler, tornado.web.StaticFileHandler):
    def prepare(self):
        if self.current_user:
            self.redirect("/indexChart.html")


def on_connect_MQTT(client, userdata, flags, rc):
    app_log.debug("Connected with result code "+str(rc))
    client.subscribe(cfg["mqtt"]["room_name"] + "/" + cfg["mqtt"]["listen_topic"])


def on_message_MQTT(client, userdata, msg):
    msg_str = msg.payload.decode('utf-8')
    app_log.debug("MQTT: " + msg.topic + " " + msg_str)
    
    try:
        data = json.loads(msg_str)
    except:
        app_log.error("E: Error when parsing message")
        return

    if not len(data) == 3: 
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
            data["team_name"]   = str(data["team_name"]) 
            data["created_on"] = str(data["created_on"])
            data["temperature"] = float(data["temperature"])                                                          # temperature should be float
        except Exception as err:   
            app_log.error("E: Error when parsing message")
            app_log.error(str(err))
            return

        try:
            data["created_on"] = utils.fix_isoformat(data["created_on"])     # correct isoformat
        except Exception as err:   # ValueError
            app_log.error("E: Can't parse time {}".format(data["created_on"]))
            app_log.error(str(err))
            return

        data["response_type"] = "temperature_data"
        final_msg = json.dumps(data)
        
        #print("Final datapoint: " + final_msg)
        #if db_connected:
        app_log.debug(database.write_message(msg_str))                # save to db

        sensor_status[data["team_name"]] = dt.datetime.now(timezone.utc)        # last online = now
         
         
        app.send_ws_message(final_msg)                            # push to frontend

        if not test_mode:
            if aimtec_connected and data["team_name"] == cfg["team"]:   # send our team's data to Aimtec
                aimtec.write_message(msg_str)
                if(data["temperature"] > aimtec.sensor.max_temperature or data["temperature"] < aimtec.sensor.min_temperature):
                    app_log.debug("ALERT SENT: " + msg_str + " " + str(aimtec.send_alert(msg_str)))
        

    


class ReceiveImageHandler(tornado.web.RequestHandler):
    def post(self):
        try:
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
        except Exception as err:
            app_log.error("E: Can't parse image")
            app_log.error(str(err))





class WebApp(TornadoApplication):

    def __init__(self, cookie_secret, database):
        self.ws_clients = []

        self.database = database

        self.tornado_handlers = [
            (r'/', RootHandler),
            (r'/index\.html', RootHandler),
            (r'/CSS/(.*)', tornado.web.StaticFileHandler, {'path': './Static/CSS'}),
            (r'/js/(.*)', tornado.web.StaticFileHandler, {'path': './Static/js'}),
            (r'/images/(.*)', tornado.web.StaticFileHandler, {'path': './Static/images'}),
            (r'/login/(.*)', LoginHandler, {'path': './login'}),
            (r'/(indexContact\.html)', tornado.web.StaticFileHandler, {'path': './Static'}),
            (r'/logout', LogoutHandler),
            (r"/receive_image", ReceiveImageHandler),
            (r"/recognize", RecognizeImageHandler),
            (r'/data', WSHandler),
            (r'/(.*)', StaticUserHandler, {'path': './Static'})  # StaticUserHandler
        ]
        self.tornado_settings = {
            "debug": True,
            "autoreload": True,
            "cookie_secret": cookie_secret,
            "login_url": "/login/faceid.html"
        }
        TornadoApplication.__init__(self, self.tornado_handlers, **self.tornado_settings)

    def send_ws_message(self, message):
            for client in self.ws_clients:
                try:
                    iol.spawn_callback(client.try_send_message, message)
                except Exception as err:
                    self.ws_clients.remove(client)
                    app_log.error("E: Can't send WS message")
                    app_log.error(str(err))





if __name__ == '__main__':
    
    config = open("config.json", "r")   # load parameters
    cfg = json.load(config)
    config.close()

    if test_mode:
        print("TEST MODE ENABLED")

    tornado.log.enable_pretty_logging()
    app_log = logging.getLogger("tornado.application")
    app_log.setLevel(logging.DEBUG)

    mqtt_client_id = "observer" + str(random.randint(10000000, 999999999999))
    mqtt_room_name = cfg["mqtt"]["room_name"]

    team_list = ["red", "blue", "black", "pink", "green"]
    sensor_status = {name:None for name in team_list}

    loader = T.Loader("./Static/")
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

    app = WebApp(bytes(cfg["cookie_secret"].encode('utf-8')), database)
    
    
    ssl_options={
        "certfile": "./letsencrypt/cert.pem",
        "keyfile": "./letsencrypt/key.pem",
        "ca_certs": "./letsencrypt/fullchain.pem",
    }
    if test_mode:
        ssl_options = None


    http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_options)    # ssl_options=ssl_options
    if test_mode == True:
        http_server.listen(80)
    else:
        http_server.listen(443)


    iol = IOLoop.current()
    print('Webserver: Initialized...')
    iol.start()




