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
from openapi_client.model.alert import Alert
from openapi_client.model.alert_body import AlertBody
from openapi_client.model.alerts import Alerts
from openapi_client.model.error import Error


class AlertsApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client
        self.create_alert_endpoint = _Endpoint(
            settings={
                'response_type': None,
                'auth': [],
                'endpoint_path': '/alerts',
                'operation_id': 'create_alert',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'team_uuid',
                    'alert',
                ],
                'required': [
                    'team_uuid',
                    'alert',
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
                    'alert':
                        (Alert,),
                },
                'attribute_map': {
                    'team_uuid': 'teamUUID',
                },
                'location_map': {
                    'team_uuid': 'header',
                    'alert': 'body',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [
                    'application/json'
                ]
            },
            api_client=api_client
        )
        self.delete_alert_endpoint = _Endpoint(
            settings={
                'response_type': None,
                'auth': [],
                'endpoint_path': '/alerts/{alertId}',
                'operation_id': 'delete_alert',
                'http_method': 'DELETE',
                'servers': None,
            },
            params_map={
                'all': [
                    'alert_id',
                    'team_uuid',
                ],
                'required': [
                    'alert_id',
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
                    'alert_id':
                        (str,),
                    'team_uuid':
                        (str,),
                },
                'attribute_map': {
                    'alert_id': 'alertId',
                    'team_uuid': 'teamUUID',
                },
                'location_map': {
                    'alert_id': 'path',
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
        self.read_all_alerts_endpoint = _Endpoint(
            settings={
                'response_type': (Alerts,),
                'auth': [],
                'endpoint_path': '/alerts',
                'operation_id': 'read_all_alerts',
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
        self.read_single_alert_endpoint = _Endpoint(
            settings={
                'response_type': (AlertBody,),
                'auth': [],
                'endpoint_path': '/alerts/{alertId}',
                'operation_id': 'read_single_alert',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'alert_id',
                    'team_uuid',
                ],
                'required': [
                    'alert_id',
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
                    'alert_id':
                        (str,),
                    'team_uuid':
                        (str,),
                },
                'attribute_map': {
                    'alert_id': 'alertId',
                    'team_uuid': 'teamUUID',
                },
                'location_map': {
                    'alert_id': 'path',
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
        self.update_alert_endpoint = _Endpoint(
            settings={
                'response_type': (AlertBody,),
                'auth': [],
                'endpoint_path': '/alerts/{alertId}',
                'operation_id': 'update_alert',
                'http_method': 'PUT',
                'servers': None,
            },
            params_map={
                'all': [
                    'alert_id',
                    'team_uuid',
                    'alert_body',
                ],
                'required': [
                    'alert_id',
                    'team_uuid',
                    'alert_body',
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
                    'alert_id':
                        (str,),
                    'team_uuid':
                        (str,),
                    'alert_body':
                        (AlertBody,),
                },
                'attribute_map': {
                    'alert_id': 'alertId',
                    'team_uuid': 'teamUUID',
                },
                'location_map': {
                    'alert_id': 'path',
                    'team_uuid': 'header',
                    'alert_body': 'body',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [
                    'application/json'
                ]
            },
            api_client=api_client
        )

    def create_alert(
        self,
        team_uuid,
        alert,
        **kwargs
    ):
        """Store an alert  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.create_alert(team_uuid, alert, async_req=True)
        >>> result = thread.get()

        Args:
            team_uuid (str): Authorize by the teamUUID of your team
            alert (Alert): Alert body

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
            None
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
        kwargs['alert'] = \
            alert
        return self.create_alert_endpoint.call_with_http_info(**kwargs)

    def delete_alert(
        self,
        alert_id,
        team_uuid,
        **kwargs
    ):
        """Delete a specific alert  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.delete_alert(alert_id, team_uuid, async_req=True)
        >>> result = thread.get()

        Args:
            alert_id (str): The id of the alert to delete
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
            None
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
        kwargs['alert_id'] = \
            alert_id
        kwargs['team_uuid'] = \
            team_uuid
        return self.delete_alert_endpoint.call_with_http_info(**kwargs)

    def read_all_alerts(
        self,
        team_uuid,
        **kwargs
    ):
        """List all alerts  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.read_all_alerts(team_uuid, async_req=True)
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
            Alerts
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
        return self.read_all_alerts_endpoint.call_with_http_info(**kwargs)

    def read_single_alert(
        self,
        alert_id,
        team_uuid,
        **kwargs
    ):
        """Read a specific alert  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.read_single_alert(alert_id, team_uuid, async_req=True)
        >>> result = thread.get()

        Args:
            alert_id (str): The id of the alert to retrieve
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
            AlertBody
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
        kwargs['alert_id'] = \
            alert_id
        kwargs['team_uuid'] = \
            team_uuid
        return self.read_single_alert_endpoint.call_with_http_info(**kwargs)

    def update_alert(
        self,
        alert_id,
        team_uuid,
        alert_body,
        **kwargs
    ):
        """Update a specific alert  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.update_alert(alert_id, team_uuid, alert_body, async_req=True)
        >>> result = thread.get()

        Args:
            alert_id (str): The id of the alert to update
            team_uuid (str): Authorize by the teamUUID of your team
            alert_body (AlertBody): Alert body

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
            AlertBody
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
        kwargs['alert_id'] = \
            alert_id
        kwargs['team_uuid'] = \
            team_uuid
        kwargs['alert_body'] = \
            alert_body
        return self.update_alert_endpoint.call_with_http_info(**kwargs)

