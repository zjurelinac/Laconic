"""
App region

...

Copyright:  (c) Zvonimir Jurelinac 2018
License:    MIT, see LICENSE for more details
"""

import functools

from .routing import Endpoint
from .util import AttributeScope, SortedList


class Region:
    """"""

    #__slots__ = []

    def __init__(self, name, routes=None, **kwargs):
        self._name = name

        self._endpoints = {}
        self._subregions = {}
        self._attrs = AttributeScope(exception_handlers=[], **kwargs)

        if routes is not None:
            self.add_routes(routes)

    # Methods for adding regions, routes and exception handlers

    def add_region(self, ):
        """"""

    def add_regions(self, regions):
        """"""
        for ... in regions:
            self.add_region(...)

    def add_route(self, url_rule, endpoint, methods=None, **kwargs):
        """"""

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

    def route(self, url_rule, methods=None, **kwargs):
        """"""
        def _decorator(func):
            self.add_route(url_rule, func, methods, **kwargs)

            @functools.wraps(func)
            def _decorated(*args, **kwargs):
                func(*args, **kwargs)
            return _decorated

        return _decorator

    def get(self, url_rule, **kwargs):
        """"""
        def _decorator(func):
            self.add_route(url_rule, func, ['GET'], **kwargs)

            @functools.wraps(func)
            def _decorated(*args, **kwargs):
                func(*args, **kwargs)
            return _decorated

        return _decorator

    def post(self, url_rule, **kwargs):
        """"""
        def _decorator(func):
            self.add_route(url_rule, func, ['POST'], **kwargs)

            @functools.wraps(func)
            def _decorated(*args, **kwargs):
                func(*args, **kwargs)
            return _decorated

        return _decorator

    def put(self, url_rule, **kwargs):
        """"""
        def _decorator(func):
            self.add_route(url_rule, func, ['PUT'], **kwargs)

            @functools.wraps(func)
            def _decorated(*args, **kwargs):
                func(*args, **kwargs)
            return _decorated

        return _decorator

    def delete(self, url_rule, **kwargs):
        """"""
        def _decorator(func):
            self.add_route(url_rule, func, ['DELETE'], **kwargs)

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


