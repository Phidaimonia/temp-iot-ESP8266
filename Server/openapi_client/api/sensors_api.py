"""
    Envi Server

    Server pro účely předmětu ZČU KKY/ITE 2021  # noqa: E501

    The version of the OpenAPI document: 1.2.1
    Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401
import sys  # noqa: F401

from openapi_client.api_client import ApiClient, Endpoint as _Endpoint
from openapi_client.model_utils import (  # noqa: F401
    check_allowed_values,
    check_validations,
    date,
    datetime,
    file_type,
    none_type,
    validate_and_convert_types
)
from openapi_client.model.error import Error
from openapi_client.model.sensors import Sensors


class SensorsApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client
        self.read_all_sensors_endpoint = _Endpoint(
            settings={
                'response_type': (Sensors,),
                'auth': [],
                'endpoint_path': '/sensors',
                'operation_id': 'read_all_sensors',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'team_uuid',
                ],
                'required': [
                    'team_uuid',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'team_uuid':
                        (str,),
                },
                'attribute_map': {
                    'team_uuid': 'teamUUID',
                },
                'location_map': {
                    'team_uuid': 'header',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client
        )

    def read_all_sensors(
        self,
        team_uuid,
        **kwargs
    ):
        """List all sensors  # noqa: E501

        List sensors available for the current team (authorized by the teamUUID in the request's header). Use the sensorUUID from the response to identify the particular sensor in the subsequent API calls.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.read_all_sensors(team_uuid, async_req=True)
        >>> result = thread.get()

        Args:
            team_uuid (str): Authorize by the teamUUID of your team

        Keyword Args:
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            Sensors
                If the method is called asynchronously, returns the request
                thread.
        """
        kwargs['async_req'] = kwargs.get(
            'async_req', False
        )
        kwargs['_return_http_data_only'] = kwargs.get(
            '_return_http_data_only', True
        )
        kwargs['_preload_content'] = kwargs.get(
            '_preload_content', True
        )
        kwargs['_request_timeout'] = kwargs.get(
            '_request_timeout', None
        )
        kwargs['_check_input_type'] = kwargs.get(
            '_check_input_type', True
        )
        kwargs['_check_return_type'] = kwargs.get(
            '_check_return_type', True
        )
        kwargs['_host_index'] = kwargs.get('_host_index')
        kwargs['team_uuid'] = \
            team_uuid
        return self.read_all_sensors_endpoint.call_with_http_info(**kwargs)
