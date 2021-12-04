
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from .api.alerts_api import AlertsApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from openapi_client.api.alerts_api import AlertsApi
from openapi_client.api.authentication_api import AuthenticationApi
from openapi_client.api.measurements_api import MeasurementsApi
from openapi_client.api.sensors_api import SensorsApi
