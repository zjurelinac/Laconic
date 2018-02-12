"""
Laconic app, a WSGI application and central object of each app or API

...

Copyright:  (c) Zvonimir Jurelinac 2018
License:    MIT, see LICENSE for more details
"""

import enum

from .context import BaseContext
from .http import Request, Response
from .region import BaseRegion
from .routing import UrlRouter
from .util import Namespace, ImmutableDict


class EventPriority(enum.Enum):
    CRITICAL = 9
    VERY_HIGH = 8
    HIGH = 7
    ABOVE_NORMAL = 6
    NORMAL = 5
    BELOW_NORMAL = 4
    LOW = 3
    VERY_LOW = 2
    LOWEST = 1


class LaconicBase(BaseRegion):
    """"""

    #__slots__ = ['context_class', 'router_class']

    # Class in use for request-processing context
    context_class = None

    # Class in use for routing
    router_class = None

    default_config = ImmutableDict({
        'DEBUG': False,
        'HTTP_AUTOMATIC_OPTIONS_RESPONSE': True,
        'HTTP_OPTIONS_RESPONSE_BODY': False
    })

    def __init__(self, name, config=None, extensions=None, logger=None,
                 endpoints=None, regions=None, **app_attrs):
        """"""
        super().__init__(name, endpoints, regions, **app_attrs)

        self.resources = Namespace()

    # def add_event_hook(self, event_name, event_hook, hook_priority=None):
    #     """"""


    # def add_event_hooks(self, event_hooks):
    #     """"""
#         for event_name, event_hook, *event_priority in event_hooks:
#             self.add_event_hook(event_name, event_hook, event_priority or None)

#     # Decorators for adding event hooks


# class Laconic(LaconicBase):
#     """
#     """


#     def __init__(self, ):
#         pass

#     # WSGI


#     # Utils

#     def __repr__(self):
#         return ''


# class LaconicRPC(LaconicBase):
#     pass
