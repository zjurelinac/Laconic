"""
HTTP request and response objects

...

Copyright:  (c) Zvonimir Jurelinac 2018
License:    MIT, see LICENSE for more details
"""

import json

from werkzeug.wrappers import BaseRequest, AcceptMixin, ETagRequestMixin, \
    AuthorizationMixin, CommonRequestDescriptorsMixin, \
    BaseResponse, CommonResponseDescriptorsMixin, \
    ETagResponseMixin

from .util import CombinedDict


# Utility constants

_missing = object()  # A sentinel value representing missing cache


# HTTP data structures

class Request(BaseRequest, CommonRequestDescriptorsMixin, ETagRequestMixin,
              AuthorizationMixin, AcceptMixin):
    """
    WSGI request wrapper object, contains data about the received request.

    Inherits from werkzeug.wrappers.BaseRequest and various mixins.
    """

    @property
    def is_json(self):
        """
        Test if the request carries JSON data (by looking at the
        `Content-Type` HTTP header)
        """
        return (self.mimetype == 'application/json') or \
               (self.mimetype.startswith('application/') and
                self.mimetype.endswith('+json'))

    @property
    def json(self):
        """
        Parse the JSON request data and return it.

        If the request doesn't contain JSON data, it will return `None`.
        """

        json_data = getattr(self, '_cached_json', _missing)
        if json_data is not _missing:
            return json_data

        request_charset = self.mimetype_params.get('charset')
        try:
            if request_charset is not None:
                json_data = json.loads(self.get_data(as_text=True),
                                       encoding=request_charset)
            else:
                json_data = json.loads(self.get_data(as_text=True))
            self._cached_json = json_data
            return json_data
        except ValueError:
            pass

    @property
    def param(self):
        """
        Combined dictionary containing all request parameters except headers
        """
        if not hasattr(self, '_param'):
            locations = [self.args, self.cookies]
            if self.method in ('POST', 'PUT', 'PATCH'):
                locations = [self.json, self.form, self.files] + locations
            self._param = CombinedDict(locations)
        return self._param


class Response(BaseResponse, CommonResponseDescriptorsMixin, ETagResponseMixin):
    """
    WSGI response wrapper object, contains data about the generated response.

    Inherits from werkzeug.wrappers.BaseResponse and various mixins.
    """
