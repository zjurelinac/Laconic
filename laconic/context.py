"""
Request-processing context

...

Copyright:  (c) Zvonimir Jurelinac 2018
License:    MIT, see LICENSE for more details
"""


import enum

from .http import BaseRequest, BaseResponse
from .util import Namespace


class CState(enum.Enum):
    """Possible context states"""
    CONTEXT_CREATED = 1
    CONTEXT_INITIALIZED = 2
    REQUEST_PROCESSED = 3
    ENDPOINT_DETERMINED = 4
    RESPONSE_GENERATED = 5
    CONTEXT_CLEANED = 6


class BaseContext:
    """"""

    __slots__ = [
        'app', '_environ', 'request', 'endpoint', 'response', 'resources',
        '_exception', '_state'
    ]

    # Class in use for request objects
    request_class = BaseRequest

    # Class in use for response objects
    response_class = BaseResponse

    

    # Context creation, initialization and cleanup

    def __init__(self, app, environ):
        self.app = app
        self._environ = environ
        
        self.request = None
        self.endpoint = None
        self.response = None
        self.resources = Namespace()

        self._exception = None
        self._state = CState.CONTEXT_CREATED

    def __enter__(self):

        # Call on_context_init handlers

        return self

    def __exit__(self, exc_type, exc_value, exc_trace):
        if exc_type is not None:
            # TODO: handle the exception

            return True
        else:
            pass

    # State transition actions

    def _process_request(self):
        pass

    def _determine_endpoint(self):
        pass
    
    def _dispatch_request(self):
        pass


# class Context(BaseContext):
#     """
#     """

#     # Class in use for request objects
#     request_class = Request

#     # Class in use for response objects
#     response_class = Response


#     #__slots__ = ['_app', '_environ', '_request', '_response', '_endpoint', '_exception']

#     def __init__(self, app, environ):
#         self._app = app
#         self._environ = environ

#         self._request = None
#         self._endpoint = None
#         self._response = None

#         self._exception = None


