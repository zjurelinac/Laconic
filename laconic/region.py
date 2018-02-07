"""
App region.

This module defines the app region, a group of related endpoints forming a
distinct part of the app, identified by a common URL prefix.

Classes:
    Region - The app region class


Copyright:  (c) Zvonimir Jurelinac 2018
License:    MIT, see LICENSE for more details
"""

import functools

from collections.abc import Sequence

from .routing import Endpoint
from .util import AttributeScope, SortedList


class Region:
    """The Region object groups a set of related endpoints in a single whole.

    Endpoints belonging to the same group share a common URL prefix (potentially
    with variable URL sections), and can have shared configuration parameters,
    error handlers etc.

    Attributes:
        name (str): The name of the app region
        routes (Sequence): A sequence of routes belonging to this region
            (a shorthand definition). Each route is defined as a tuple ()
        exc_handlers (Sequence): A sequence of exception handlers for this
            region
        **kwargs: Optional configuration parameters shared between all routes
            belonging to this region
    """

    #__slots__ = []

    def __init__(self, name, routes=None, exc_handlers=None, **kwargs):
        self.name = name

        self.routes = {}
        self.subregions = {}
        # self._exception_handlers =
        self.attrs = AttributeScope(**kwargs)

        if routes is not None:
            self.add_routes(routes)

        if exception_handlers is not None:
            self.add_exception_handlers(handlers)

    # Methods for adding regions, routes and exception handlers

    def add_region(self, region):
        """"""

    def add_regions(self, regions):
        """"""
        for ... in regions:
            self.add_region(...)

    def add_route(self, url_rule, endpoint, methods=None, **kwargs):
        """"""
        self.routes.append((url_rule, methods, Endpoint(endpoint, **kwargs)))

    def add_routes(self, routes):
        """"""
        for url_rule, endpoint, methods, attrs in routes:
            self.add_route(url_rule, endpoint, methods, **attrs)

    def add_exception_handler(self, exc_type, exc_handler):
        """"""

    def add_exception_handlers(self, exc_handlers):
        """"""
        for exc_type, exc_handler in exc_handlers:
            self.add_exception_handler(exc_type, exc_handler)

    # Decorators for adding routes and exception handlers

    def route(self, url_rule, methods=None, name=None, **kwargs):
        """"""
        def _decorator(func):
            self.add_route(url_rule, func, methods, name, **kwargs)

            @functools.wraps(func)
            def _decorated(*args, **kwargs):
                func(*args, **kwargs)
            return _decorated

        return _decorator

    def get(self, url_rule, name=None, **kwargs):
        """"""
        def _decorator(func):
            self.add_route(url_rule, func, ['GET'], name, **kwargs)

            @functools.wraps(func)
            def _decorated(*args, **kwargs):
                func(*args, **kwargs)
            return _decorated

        return _decorator

    def post(self, url_rule, name=None, **kwargs):
        """"""
        def _decorator(func):
            self.add_route(url_rule, func, ['POST'], name, **kwargs)

            @functools.wraps(func)
            def _decorated(*args, **kwargs):
                func(*args, **kwargs)
            return _decorated

        return _decorator

    def put(self, url_rule, name=None, **kwargs):
        """"""
        def _decorator(func):
            self.add_route(url_rule, func, ['PUT'], name, **kwargs)

            @functools.wraps(func)
            def _decorated(*args, **kwargs):
                func(*args, **kwargs)
            return _decorated

        return _decorator

    def delete(self, url_rule, name=None, **kwargs):
        """"""
        def _decorator(func):
            self.add_route(url_rule, func, name, ['DELETE'], **kwargs)

            @functools.wraps(func)
            def _decorated(*args, **kwargs):
                func(*args, **kwargs)
            return _decorated

        return _decorator

    def exception(self, exc_type):
        """"""
        def _decorator(func):
            self.add_exception_handler(exc_type, func)

            @functools.wraps(func)
            def _decorated(*args, **kwargs):
                func(*args, **kwargs)
            return _decorated

        return _decorator


