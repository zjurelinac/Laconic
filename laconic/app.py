"""
Laconic app, a WSGI application and central object of each app or API

...

Copyright:  (c) Zvonimir Jurelinac 2018
License:    MIT, see LICENSE for more details
"""

from .context import Context
from .http import Request, Response
from .region import Region
from .routing import Router


class Laconic(Region):
    """
    """

    #__slots__ = ['request_class', 'response_class', 'context_class', 'router_class'] + Region.__slots__

    # Class in use for request objects
    request_class = Request

    # Class in use for response objects
    response_class = Response

    # Class in use for request-processing context
    context_class = Context

    # Class in use for routing
    router_class = Router

    def __init__(self, ):
        pass

    # Methods for adding event hooks

    def add_event_hook(self, event_name, event_hook, hook_priority=None):
        """"""

    def add_event_hooks(self, event_hooks):
        """"""
        for event_name, event_hook, *event_priority in event_hooks:
            self.add_event_hook(event_name, event_hook, event_priority or None)

    # Decorators for adding event hooks


    # WSGI

