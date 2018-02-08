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
        routes (list): A list of routes 
    """

    __slots__ = ['name', 'routes', 'subregions', 'attrs', ]

    def __init__(self, name: str, regions: Sequence=None, routes: Sequence=None, exc_handlers: Sequence=None, **config_params):
        """Region object constructor.

        Constructs an app region identified by its `name`, optionally registeres provided
        routes and exception handlers, and stores given configuration parameters.
        
        Args:
            name (str): The name of the app region
            regions (optional, Sequence): A sequence of regions to be added to this region as
                subregions (their )
            routes (optional, Sequence): A sequence of routes to be added to this region
                (a shorthand definition). Each route is defined as a tuple:
                   `(url_rule, endpoint, [methods: list], [name: str], [params: dict])`
            exc_handlers (optional, Sequence): A sequence of exception handlers for this
                region. Each handler is defined as a tuple: `(exc_type, handler)`
            **config_params: Optional configuration parameters shared between all routes
                belonging to this region
        """
        self.name = name

        self.routes = {}
        self.subregions = {}

        self.attrs = AttributeScope(**config_params)

        if regions is not None:
            self.add_regions(regions)

        if routes is not None:
            self.add_routes(routes)

        # if exception_handlers is not None:
        #     self.add_exception_handlers(handlers)

    # Methods for adding regions, routes and exception handlers

    def add_region(self, region: Region, url_prefix: str=None):
        """Add a subregion to the app region.
        
        TODO: Document add_region!

        Args:
            region (Region):
            url_prefix (optional, str):
        """
        self.subregions[(region.name, url_prefix)] = region

    def add_regions(self, regions: Sequence):
        """Add multiple subregions to the app region.
        
        TODO: Document add_regions!

        Args:
            regions (Sequence): 
        """
        for region, *url_prefix in regions:
            self.add_region(region, url_prefix or None)

    def add_route(self, url_rule: str, endpoint: Callable, methods: Sequence=None, name: str=None,
            **config_params):
        """Add a route to the app region.
        
        Registers a route to the region at a specified URL (potentially parametrized), which
        will respond to all requests having any of provided `methods` (if not set, default: GET).
        It also allows setting route specific configuration parameters via keyword-only arguments.

        URL rules support parametrized URL sections defined as `../<param_name:param_type>/..`
        (e.g. '/users/<id:int>'), with `param_type` being one of the following:
            - string - any text without a slash (the default type)
            - int - any (unsigned) integer
            - float - any floating-point number
            - path - any text, can include slashes

        The callable's parameters should be tagged with Python type hints to enable parameter type
        deduction and validation (otherwise, all parameters will be considered to be strings).
        Alternatively, a special decorator can be used to manually set parameter types and
        constraints (TODO: Route param decorator)

        Args:
            url_rule (str): An URL rule defining the URL paths for which this endpoint will receive
                requests
            endpoint (Callable): Any Python callable (a function, method, custom callable object...)
                which will be called to process requests for a given route.
            methods (optional, Sequence): A sequence of uppercase strings listing all HTTP methods
                this endpoint will support (possible element values: GET, POST, PUT, DELETE, PATCH,
                HEAD, OPTIONS)
            name (optional, str): A custom name assigned to this route (by default, it is the
                endpoint function/method name)
            **config_params: Optional configuration parameters for this endpoint

        Raises:
            xyz - Invalid route definition?
        """
        self.routes.append((url_rule, methods, Endpoint(endpoint, name=name, **config_params)))

    def add_routes(self, routes: Sequence):
        """Add multiple routes to the app region.
        
        Description of each route should contain at least the URL rule and the endpoint for the
        route, and optionally also the list of supported methods (by default only GET is supported),
        route name (by default the endpoint function/method name), and a dictionary containing route
        configuration parameters. For more info on expected URL rule format, as well as other
        parameters, see documentation for `add_route` method.

        Args:
            routes (Sequence): A sequence (list, tuple) of routes to be added to the region.
                Each route should be defined as a tuple:
                    `(url_rule, endpoint, [methods: list | tuple], [name: str], [params: dict])`

        Raises:
            xyz - Invalid route definition?
        """
        for route_def in routes:
            if not isinstance(route_def, tuple):
                raise TypeError('Route definition should be a tuple: %s.' % route_def)
            
            if len(route_def) < 2:
                raise ValueError('Incorrect route definition (should contain at least'
                                 'the URL and endpoint): %s' % route_def)

            url_rule = route_def[0]
            endpoint = route_def[1]
            
            methods, name, attrs = None, None, None
            
            for item in route_def[2:]
                if isinstance(item, str) and name is None:
                    name = item
                elif isinstance(item, list, tuple) and methods is None:
                    methods = item
                elif isinstance(item, dict) and attrs is None:
                    attrs = item
                else:
                    raise TypeError('Incorrect route definition (cannot recognize part: %s): %s'
                                    % (item, route_def))

            # TODO: Except potential errors and notify which route caused it
            self.add_route(url_rule, endpoint, methods=methods, name=name, **(attrs or {}))

    # def add_exception_handler(self, exc_type, exc_handler):
    #     """"""

    # def add_exception_handlers(self, exc_handlers):
    #     """"""
    #     for exc_type, exc_handler in exc_handlers:
    #         self.add_exception_handler(exc_type, exc_handler)

    # Decorators for adding routes and exception handlers

    def route(self, url_rule: str, methods: Sequence=None, name: str=None, **config_params):
        """Shortcut decorator for `add_route` method.
        
        For detailed arguments description, see `add_route` documentation.

        Args:
            url_rule (str): An URL rule defining the URL paths for which this endpoint will receive
                requests
            methods (optional, Sequence): A sequence of uppercase strings listing all HTTP methods
                this endpoint will support
            name (optional, str): A custom name assigned to this route (by default, it is the
                endpoint function/method name)
            **config_params: Optional configuration parameters for this endpoint
        """
        def _decorator(func):
            self.add_route(url_rule, func, methods, name, **kwargs)

            @functools.wraps(func)
            def _decorated(*args, **kwargs):
                func(*args, **kwargs)
            return _decorated

        return _decorator

    def get(self, url_rule: str, name: str=None, **config_params):
        """Shortcut decorator for `add_route(..., methods=['GET'], ...)`.
        
        For detailed arguments description, see `add_route` documentation.

        Args:
            url_rule (str): An URL rule defining the URL paths for which this endpoint will receive
                requests
            name (optional, str): A custom name assigned to this route (by default, it is the
                endpoint function/method name)
            **config_params: Optional configuration parameters for this endpoint
        """
        def _decorator(func):
            self.add_route(url_rule, func, ['GET'], name, **kwargs)

            @functools.wraps(func)
            def _decorated(*args, **kwargs):
                func(*args, **kwargs)
            return _decorated

        return _decorator

    def post(self, url_rule: str, name: str=None, **config_params):
        """Shortcut decorator for `add_route(..., methods=['POST'], ...)`.
        
        For detailed arguments description, see `add_route` documentation.

        Args:
            url_rule (str): An URL rule defining the URL paths for which this endpoint will receive
                requests
            name (optional, str): A custom name assigned to this route (by default, it is the
                endpoint function/method name)
            **config_params: Optional configuration parameters for this endpoint"""
        def _decorator(func):
            self.add_route(url_rule, func, ['POST'], name, **kwargs)

            @functools.wraps(func)
            def _decorated(*args, **kwargs):
                func(*args, **kwargs)
            return _decorated

        return _decorator

    def put(self, url_rule: str, name: str=None, **config_params):
        """Shortcut decorator for `add_route(..., methods=['PUT'], ...)`.
        
        For detailed arguments description, see `add_route` documentation.

        Args:
            url_rule (str): An URL rule defining the URL paths for which this endpoint will receive
                requests
            name (optional, str): A custom name assigned to this route (by default, it is the
                endpoint function/method name)
            **config_params: Optional configuration parameters for this endpoint"""
        def _decorator(func):
            self.add_route(url_rule, func, ['PUT'], name, **kwargs)

            @functools.wraps(func)
            def _decorated(*args, **kwargs):
                func(*args, **kwargs)
            return _decorated

        return _decorator

    def delete(self, url_rule: str, name: str=None, **config_params):
        """Shortcut decorator for `add_route(..., methods=['DELETE'], ...)`.
        
        For detailed arguments description, see `add_route` documentation.

        Args:
            url_rule (str): An URL rule defining the URL paths for which this endpoint will receive
                requests
            name (optional, str): A custom name assigned to this route (by default, it is the
                endpoint function/method name)
            **config_params: Optional configuration parameters for this endpoint"""
        def _decorator(func):
            self.add_route(url_rule, func, name, ['DELETE'], **kwargs)

            @functools.wraps(func)
            def _decorated(*args, **kwargs):
                func(*args, **kwargs)
            return _decorated

        return _decorator

    # def exception(self, exc_type):
    #     """"""
    #     def _decorator(func):
    #         self.add_exception_handler(exc_type, func)

    #         @functools.wraps(func)
    #         def _decorated(*args, **kwargs):
    #             func(*args, **kwargs)
    #         return _decorated

    #     return _decorator


