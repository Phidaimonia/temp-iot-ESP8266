import psycopg2
import json
import datetime
import time
import pytz
import utils

from user import User


class DB:
    """
    A class used to instantiate a DB connection and save messages into a table 'sensor_data'

    Attributes
    ----------
    log : callable
        A method used to log debug and error messages

    Methods
    -------
    write_message(msg)
        Saves the measurement in the msg to the database
    """
    def __init__(self, logger = print):
        self.log = logger
        self.connected = False
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
        
        self.__connect()

    def __del__(self):
        try:
            self.connected = False
            self.cursor.close()
            self.conn.close()
        except:
            pass
        if self.connected:
            self.log("D: Closed connection with the database.")

    def __connect(self):
        try:    
            self.conn = psycopg2.connect(self.cfg["CONNECTION"])
        except psycopg2.OperationalError as err:
            self.log("E: Unable to connect to the database.")
            self.connected = False
            self.cursor = None
            return
        self.log("D: Successfully connected to the database.")
        self.cursor = self.conn.cursor()
        self.connected = True

    def write_message(self, msg):
        """
        Saves the measurement in the msg to the database

        Parameters
        ----------
        msg : str
            JSON formatted MQTT message. eg.: {'team_name': 'white', 'created_on': '2020-03-24T15:26:05.336974', 'temperature': 25.72} 

        Returns
        -------
        int
            returns 0 if it is impossible to save the data into the database, 1 if the data were saved successfully
        """
        INSERT = """INSERT INTO sensor_data (time, sensor_id, temperature) VALUES
                                    (%s, (SELECT id from sensors WHERE team=%s), %s);"""

        for trial in range(3):
            if not self.connected:
                self.__connect()
                time.sleep(5)
        
        if not self.connected:
            return 0


        try:
            measurement = json.loads(msg)
 
            measurement_time = utils.fuzzy_ISO_to_datetime(measurement["created_on"]) # expecting UTC time
            team = measurement["team_name"]
            temperature = measurement["temperature"]
            data = (measurement_time, team, temperature)

        except json.JSONDecodeError as err:
            self.log("E: Message {0} is not a json.".format(msg))
            self.log("   " + str(err))
            return 0
        except KeyError as err:
            self.log("E: Missing measurement attribute in message: {0}.".format(msg))
            self.log("   " + str(err))
            return 0
        except ValueError as err:
            self.log("E: Invalid datetime string: {0}".format(measurement["created_on"]))
            self.log("   "+str(err))
            return 0

        for i in range(3):
            try:
                self.cursor.execute(INSERT, data)
                self.conn.commit()
                #self.log("D: Successfully saved the message: {0}".format(msg))
                return 1
            except psycopg2.OperationalError as err:
                self.log("E: Lost connection to DB. Trying to reconnect. Attempts left:" + str(2-i))
                self.connected = False
                self.__connect()
                time.sleep(5)
                continue
            except psycopg2.IntegrityError as err:
                self.connected = False
                self.log("E: Unable to save the meassage: {0}.".format(msg))
                self.log("   " + str(err))
                break
            break
        return 0

    def getUser(self, user_id = None, username = None):
        SELECT = """SELECT u.id, u.username, u.role FROM
                        users as u
                        WHERE u.id = %s OR u.username = %s"""

        for trial in range(3):
            if not self.connected:
                self.__connect()
                time.sleep(5)
        
        if not self.connected:
            return 0

        for i in range(3): #tries to reconnect 2 times
            try:
                self.cursor.execute(SELECT, [user_id, username])
                self.conn.commit()
                self.log("D: Successfully retrieved data")
                user_data = self.cursor.fetchall()
                if len(user_data) == 0: return None
                user_id, username, role = user_data[0]
                return User(user_id, username, role)
            except psycopg2.OperationalError as err:
                self.log("E: Problem with reading from the DB, might have had lost the connection to the DB. \n   Trying to reconnect. Attempts left:" + str(2-i))
                self.connected = False
                self.__connect()
                time.sleep(5)
                continue
            break
        return None

    def read_min_max_messages(self, dt_from, dt_to, teams, interval):
        SELECT = """SELECT S.team, time_bucket(%(interval)s, D.time) AT TIME ZONE 'UTC' AS okno,
                min(D.temperature), max(D.temperature), avg(temperature)
                FROM sensor_data D LEFT JOIN sensors S ON D.sensor_id = S.id
                WHERE S.team = %(team)s AND D.time >= %(from)s AND D.time <= %(to)s
                GROUP BY okno, S.team
                ORDER BY okno;"""

        for trial in range(3):
            if not self.connected:
                self.__connect()
                time.sleep(5)
        
        if not self.connected:
            return 0

        dts = (dt_from, dt_to)

        for dt in dts: # naive dt to UTC
            if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
                dt = pytz.utc.localize(dt)

        result = []

        for team in teams:
                
            data = {"from": dt_from, "to": dt_to, "team": team, "interval": interval}

            for i in range(3): #tries to reconnect 2 times
                try:
                    self.cursor.execute(SELECT, data)
                    self.conn.commit()
                    self.log("D: Successfully retrieved data")
                    measurements = self.cursor.fetchall()
                    result.extend([{'team_name': team, 'created_on': created_on.isoformat(), 'temperature_min': minimum, 'temperature_max': maximum, 'temperature_avg': average} for team, created_on, minimum, maximum, average in measurements])
                except psycopg2.OperationalError as err:
                    self.log("E: Problem with reading from the DB, might have had lost the connection to the DB. \n   Trying to reconnect. Attempts left:" + str(2-i))
                    self.connected = False
                    self.__connect()
                    time.sleep(5)
                    continue
                except psycopg2.ProgrammingError as err:
                    self.connected = False
                    self.log(str(err))
                    self.log(self.cursor.query)
                break
        return result

    def read_messages(self, dt_from, dt_to, teams):
        """
        Fetches measurements in between dt_from and dt_to by teams in teams from the DB and returns them.

        Parameters
        ----------
        dt_from : datetime
            Fetch records from this time. Naive dt is considered to be in UTC. Inclusive
        dt_to : datetime
            Fetch records up to this time. Naive dt is considered to be in UTC. Inclusive
        teams : iterable
            Fetch measurements only by teams with their teamnames in this iterable.

        Returns
        -------
        list
            of dictionaries in the format: {'team_name': 'white', 'created_on': '2020-03-24T15:26:05.336974', 'temperature': 25.72}
        """
        SELECT = """SELECT S.team, D.time AT TIME ZONE 'UTC', D.temperature
                    FROM sensor_data D LEFT JOIN sensors S ON D.sensor_id = S.id
                    WHERE S.team IN %(teams)s AND D.time >= %(from)s AND D.time <= %(to)s
                    ORDER BY D.time;"""
        dts = (dt_from, dt_to)

        for trial in range(3):
            if not self.connected:
                self.__connect()
                time.sleep(5)
        
        if not self.connected:
            return 0

        for dt in dts: # naive dt to UTC
            if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
                dt = pytz.utc.localize(dt)
                
        data = {"from": dt_from, "to": dt_to, "teams": tuple(teams)}

        for i in range(3): #tries to reconnect 2 times
            try:
                self.cursor.execute(SELECT, data)
                self.conn.commit()
                self.log("D: Successfully retrieved data")
                measurements = self.cursor.fetchall()
                return [{'team_name': team, 'created_on': created_on.isoformat(), 'temperature': temp} for team, created_on, temp in measurements]
            except psycopg2.OperationalError as err:
                self.log("E: Problem with reading from the DB, might have had lost the connection to the DB. \n   Trying to reconnect. Attempts left:" + str(2-i))
                self.connected = False
                self.__connect()
                time.sleep(5)
                continue
            break
        return None

if __name__ == '__main__':       # tests
    db = DB()
    # for d in range(1, 15):
    #    for h in range (24):
    #        message = json.dumps({'team_name': 'pink', 'created_on': '2020-03-{0:02d}T{1:02d}:26:05.336974'.format(d, h), 'temperature': 25.72})
    #        db.write_message(message)

    data = db.read_min_max_messages(pytz.utc.localize(datetime.datetime(2021, 12, 5, 15)), pytz.utc.localize(datetime.datetime(2021, 12, 5, 16)), ['red', 'pink'], datetime.timedelta(minutes=10))
    for m in data:
        print(m)
        print("")

    #t = "2021-12-2T23:7:3.397000"
    #print(t)