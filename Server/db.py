import psycopg2
import json
import datetime
import time

class DB:
    def __init__(self, logger = print):
        self.log = logger
        try:
            config = open("config_db.json", "r")   # load parameters
            self.cfg = json.load(config)
            config.close()
        except json.JSONDecodeError as err:
            self.log("E: Invalid DB config.")
            self.log(err.msg)
            raise err
        except IOError as err:
            self.log("E: DB config does not exist.")
            raise err
        
        self.connect()

    def __del__(self):
        self.cursor.close()
        self.conn.close()
        self.log("D: Closed connection with the database.")

    def connect(self):
        try:
            self.conn = psycopg2.connect(self.cfg["CONNECTION"])
        except psycopg2.OperationalError as err:
            self.log("E: Unable to connect to the database.")
            return
        self.log("D: Successfully connected to the database.")
        self.cursor = self.conn.cursor()

    def write_message(self, msg):
        INSERT = """INSERT INTO sensor_data (time, sensor_id, temperature) VALUES
                                    (%s, (SELECT id from sensors WHERE team=%s), %s);"""
        try:
            measurement = json.loads(msg)

            measurement_time = datetime.datetime.fromisoformat(measurement["created_on"]) # expecting UTC time
            team = measurement["team_name"]
            temperature = measurement["temperature"]
            data = (measurement_time, team, temperature)

        except json.JSONDecodeError as err:
            self.log("E: Message {0} is not a json.".format(msg))
            self.log("   " + str(err))
        except KeyError as err:
            self.log("E: Missing measurement attribute in message: {0}.".format(msg))
            self.log("   " + str(err))

        for i in range(3):
            try:
                self.cursor.execute(INSERT, data)
                self.conn.commit()
                self.log("D: Successfully saved the message: {0}".format(msg))
            except psycopg2.OperationalError as err:
                self.log("E: Lost connection to DB. Trying to reconnect. Attempts left:" + str(2-i))
                self.connect()
                time.sleep(5)
                continue
            except psycopg2.IntegrityError as err:
                self.log("E: Unable to save the meassage: {0}.".format(msg))
                self.log("   " + str(err))
                break
            break

if __name__ == '__main__':
    db = DB()
    message = json.dumps({'team_name': 'pink', 'created_on': '2020-03-24T15:26:05.336974', 'temperature': 25.72})
    db.write_message(message)
