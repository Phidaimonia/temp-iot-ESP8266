import openapi_client
from openapi_client.api import alerts_api, authentication_api, measurements_api, sensors_api
from openapi_client.api_client import ApiClient
from openapi_client.model.alert import Alert
from openapi_client.model.login import Login
from openapi_client.model.measurement import Measurement
from openapi_client.model.sensors import Sensors
import json

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

        self.login()

        self.sensors()

    def login(self):
        try:
            resp = self.authentication_api.login(Login(username = self.__username, password = self.__password))
        except openapi_client.ApiException as err:
            self.log("E: Exception when calling AuthenticationApi->login: " + str(e))
            raise err
        self.team_uuid = resp.team_uuid
        self.log("D: Successfully connected to the API. Team_uuid is: " + self.team_uuid)

    def sensors(self):
        try:
            resp = self.sensors_api.read_all_sensors(self.team_uuid)
        except openapi_client.ApiException as err:
            self.log("E: Exception when calling SensorsApi->read_all_sensors: " + str(e))
            raise err
        self.sensor = resp.value[0]
        self.log("D: Successfully received sensors from the API. Sensor_uuid is: " + self.sensor.sensor_uuid)

    def write_message(self, msg):
        try:
            measurement_dict = json.loads(msg)

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
        except openapi_client.ApiException as e:
            self.log("E: Exception when calling MeasurementsApi->create_measurement: " + str(e))
if __name__ == "__main__":
    api_client = Api("Orange", ">f@9C3p<")
    api_client.write_message('{"team_name": "white", "created_on": "2021-11-27T12:25:05.336974", "temperature": 25.72}')