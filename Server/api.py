import openapi_client as openapi_client
from openapi_client.api import alerts_api, authentication_api, measurements_api, sensors_api
from openapi_client.api_client import ApiClient
from openapi_client.model.alert import Alert
from openapi_client.model.login import Login
from openapi_client.model.measurement import Measurement
from openapi_client.model.sensors import Sensors
import json, datetime


def fuzzy_ISO_to_datetime(weakISO):
    t = None
    try:
        t = datetime.datetime.fromisoformat(weakISO)
    except Exception:
        pass

    if t is None:
        t = datetime.datetime.strptime(weakISO, "%Y-%m-%dT%H:%M:%S.%f")

    return t


def fixISO(tm):
    t = fuzzy_ISO_to_datetime(tm)
    return "%04d-%02d-%02dT%02d:%02d:%09.6f" % (t.year, t.month, t.day, t.hour, t.minute, t.second)


class Api:
    def __init__(self, username, password, logger = print):
        self.__username = username
        self.__password = password
        self.log = logger
        self.api_client = ApiClient()
        self.alerts_api = alerts_api.AlertsApi(self.api_client)
        self.authentication_api = authentication_api.AuthenticationApi(self.api_client)
        self.measurements_api = measurements_api.MeasurementsApi(self.api_client)
        self.sensors_api = sensors_api.SensorsApi(self.api_client)
        self.connected = False

        self.login()
        self.sensors()

    def login(self):
        try:
            resp = self.authentication_api.login(Login(username = self.__username, password = self.__password))
        except openapi_client.ApiException as err:
            self.log("E: Exception when calling AuthenticationApi->login: " + str(err))
            raise err
        self.team_uuid = resp.team_uuid
        self.log("D: Successfully connected to the API. Team_uuid is: " + self.team_uuid)

    def sensors(self):
        try:
            resp = self.sensors_api.read_all_sensors(self.team_uuid)
        except openapi_client.ApiException as err:
            self.log("E: Exception when calling SensorsApi->read_all_sensors: " + str(err))
            self.connected = False
            raise err
        self.sensor = resp.value[0]

        if not self.connected:
            self.log("D: Successfully received sensors from the API. Sensor_uuid is: " + self.sensor.sensor_uuid)
        self.connected = True

    def is_online(self):
        try:
            self.sensors()
        except Exception:
            pass
        return self.connected

    def write_message(self, msg):
        try:
            measurement_dict = json.loads(msg)

            measurement_dict["created_on"] = fixISO(measurement_dict["created_on"])

            measurement = Measurement(
            created_on = measurement_dict["created_on"][0:-3]+"+00:00", # expecting UTC time
            sensor_uuid = self.sensor.sensor_uuid,
            temperature = measurement_dict["temperature"],
            status = "OK")

        except json.JSONDecodeError as err:
            self.log("E: Message {0} is not a json.".format(msg))
            self.log("   " + str(err))
            return 0
        except KeyError as err:
            self.log("E: Missing measurement attribute in message: {0}.".format(msg))
            self.log("   " + str(err))
            return 0

        try:
            self.measurements_api.create_measurement(self.team_uuid, measurement)
            self.log("D: Successfully sent measurement: " + msg)
            return 1
        except openapi_client.ApiException as e:
            self.log("E: Exception when calling MeasurementsApi->create_measurement: " + str(e))
            return 0

    def send_alert(self, msg = None, temperature = None, created_on = None):
        sensor_uuid = self.sensor.sensor_uuid
        high_temperature = self.sensor.max_temperature
        low_temperature = self.sensor.min_temperature

        if msg is not None:
            try:
                measurement_dict = json.loads(msg)
                measurement_dict["created_on"] = fixISO(measurement_dict["created_on"])

                created_on = measurement_dict["created_on"][0:-3]+"+00:00" # expecting UTC time
                temperature = measurement_dict["temperature"]

            except json.JSONDecodeError as err:
                self.log("E: Message {0} is not a json.".format(msg))
                self.log("   " + str(err))
                return 0
            except KeyError as err:
                self.log("E: Missing measurement attribute in message: {0}.".format(msg))
                self.log("   " + str(err))
                return 0

        if created_on is None:
            created_on = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds')
            
        if temperature is not None:
            alert = Alert(created_on, sensor_uuid, temperature, high_temperature, low_temperature)
        else:
            self.log("E: Error when creating alert. Check supplied parameters.")
            return 0

        try:
            # Store an alert
            self.alerts_api.create_alert(self.team_uuid, alert)
            return 1
        except openapi_client.ApiException as e:
            print("E: Exception when calling AlertsApi->create_alert: " + str(e))
            return 0

if __name__ == "__main__":
    api_client = Api("Orange", ">f@9C3p<")
    api_client.write_message('{"team_name": "white", "created_on": "2021-11-8T4:25:5.33", "temperature": 25.72}')