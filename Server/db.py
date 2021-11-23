import psycopg2
import json
import datetime

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
            self.log(err.msg)
            raise err
        self.conn = psycopg2.connect(cfg["CONNECTION"])
        self.cursor = conn.cursor()

    # def write_message(self, msg):
    #     INSERT = """INSERT INTO sensor_data (time, sensor_id, temperature) VALUES
    #                                 (%s, (SELECT id from sensors WHERE team=%s), %s);"""
    #     try:
    #         measurement = json.loads(msg)

    #         measurement_time = datetime.datetime.fromisoformat(measurement["created_on"]) # expecting UTC time
    #         team = measurement["team_name"]
    #         temperature = measurement["temperature"]
    #         data = (measurement_time, team, temperature)

    #         self.cursor.execute(INSERT, data)
    #         self.conn.commit()
    #     except json.JSONDecodeError as err:
    #         self.log(msg)
    #         self.log("E: Message is not a json.")
    #         self.log(err.msg)
    #     except KeyError as err:
    #         self.log(msg)
    #         self.log("E: Missing measurement attribute.")
    #         self.log(err.msg)

