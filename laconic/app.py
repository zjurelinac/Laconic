"""Laconic app, a WSGI application and central object of each app or API

...

Classes:
    EventPriority
    LaconicBase
    Laconic
    LaconicRpc

Copyright:  (c) Zvonimir Jurelinac 2018
License:    MIT, see LICENSE for more details
"""

import enum
import os

from .context import BaseContext
from .http import Request, Response
from .region import BaseRegion
from .routing import BaseRouter
from .util import Config, Namespace, ImmutableDict


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

    __slots__ = ['context_class', 'router_class', 'base_path', 'router',
                 'config', 'logger', 'extensions', 'resources', 'event_handlers']

    # Class in use for request-processing context
    context_class = BaseContext

    # Class in use for routing
    router_class = BaseRouter

    default_config = ImmutableDict({
        'DEBUG': False,
        'HTTP_AUTOMATIC_OPTIONS_RESPONSE': True,
        'HTTP_OPTIONS_RESPONSE_BODY': False
    })

    def __init__(self, name, config=None, extensions=None, logger=None,
                 endpoints=None, regions=None, **app_attrs):
        """"""
        super().__init__(name, endpoints, regions, **app_attrs)


        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.config = Config.create(config, self.default_config,
                                    base_path=self.base_path)

        self.router = self.router_class()
        self.logger = logger or self._create_default_logger()

        self.event_handlers = {}

        self.resources = Namespace()

    # Util
    
    def _create_default_logger(self):
        pass


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
