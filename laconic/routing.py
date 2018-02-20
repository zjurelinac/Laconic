"""
Laconic router and routing

...

Copyright:  (c) Zvonimir Jurelinac 2018
License:    MIT, see LICENSE for more details
"""


from .util import Dispatchable


class UrlRule:
    pass


class Endpoint(Dispatchable):
    """"""

    # __slots__ = []

    def __init__(self):
        pass


    def __call__(self, context):
        pass


class UrlEndpoint(Endpoint):
    """"""


class RpcEndpoint(Endpoint):
    """""" 


class BaseRouter:
    """"""

    def register_endpoint(self, endpoint):
        """"""

class UrlRouter(BaseRouter):
    """"""

    def register_endpoint(self, url_rule, endpoint):
        """"""


class RpcRouter(BaseRouter):
    """"""

    def register_endpoint(self, endpoint):
        """"""
