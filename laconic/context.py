"""
Request-processing context

...

Copyright:  (c) Zvonimir Jurelinac 2018
License:    MIT, see LICENSE for more details
"""

class Context:
    """
    """

    #__slots__ = ['_app', '_environ', '_request', '_response', '_endpoint', '_exception']

    def __init__(self, app, environ):
        self._app = app
        self._environ = environ

        self._request = None
        self._endpoint = None
        self._response = None

        self._exception = None


