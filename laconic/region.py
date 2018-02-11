"""
App regions.

This module defines the abstract concept of an app region as a group of related
endpoints forming a distinct part of the app. It also provides a specific
implementation of a URLRegion, which represents a group of endpoints sharing a
common URL prefix.

Classes:
    BaseRegion - Abstract app region class
    UrlRegion - URL-identified app region

Todos:
    TODO: route automatic name
    TODO: pack as many info in attribute scope as possible

    (later)
    TODO: RPCRegion

Copyright:  (c) Zvonimir Jurelinac 2018
License:    MIT, see LICENSE for more details
"""

from collections.abc import Callable, Sequence

from .routing import Endpoint
from .util import AttributeScope, Dispatchable, ExceptionHandler

class BaseRegion:
    """BaseRegion object groups a set of related endpoints in a single whole.

    A base class for more specific app region implementations. Provides means
    for defining region-specific configuration parameters (which will then apply
    to all contained routes and subregions, unless overriden) and exception
    handlers.

    Attributes:
        name (str): The name of the app region
        endpoints (list): List of all endpoints belonging to this region
        regions (list): List of all subregions added to this region
        attrs (AttributeScope): Dictionary-like object containing all region's
            configuration parameters
    """

    __slots__ = ['name', 'endpoints', 'regions', 'attrs']

    def __init__(self, name: str, **config_params):
        """BaseRegion object constructor.

        Constructs an app region identified by its `name`, and stores all passed
        configuration parameters. Available configuration parameters common to
        all types of regions are:
            exception_handlers (List[Exception, Callable]): List of handlers for
                particular exception types
            before_request (List[Callable]): List of hooks to be executed before
                each request directed to this app region. Hooks will be executed
                in order they were listed, and
            after_request (List[Callable]): List of hooks to be executed after
                each request directed to this app region

        Args:
            name (str): Name of the app region
            **config_params: Optional configuration parameters for this region
        """
        self.name = name
        self.endpoints = []
        self.regions = []
        self.attrs = AttributeScope(**config_params)

        if 'exception_handlers' not in self.attrs:
            self.attrs['exception_handlers'] = []

        if 'before_request' not in self.attrs:
            self.attrs['before_request'] = []

        if 'after_request' not in self.attrs:
            self.attrs['after_request'] = []

    def add_region(self, region):
        """Add a subregion to the app region.

        Adds an existing region as a subregion to this one. The subregion will
        inherit all configuration parameters of this region (but it can override
        them if desired).

        Args:
            region (Region): Existing app region to be added as a subregion
        """
        region.attrs.parent = self.attrs
        self.regions.append(region)

    def add_regions(self, regions: Sequence):
        """Add multiple subregions to the app region.

        For more details, see documentation of `add_region` method.

        Args:
            regions (Sequence): A sequence (list, tuple) of regions to be added
                to this region as subregions
        """
        for region in regions:
            self.add_region(region)

    def add_exception_handler(self, exc_type: type, exc_handler: Callable,
                              **config_options):
        """Add an exception handler to the region.

        Register an exception handler for handling exceptions of specified type
        that occur during processing of requests for this app region. Registered
        handler will handle all exceptions of this type and its subtypes, unless
        there is another handler defined for a more specific derived type.

        Args:
            exc_type (type): Type of exceptions this handler should handle
            exc_handler (Callable): Any Python callable, it will be called to
                handle the exception and optionally provide a response to the
                requester
            **config_options: Optional configuration parameters for the handler
        """
        self.attrs['exception_handlers'].append(
            ExceptionHandler(exc_type, exc_handler,
                             AttributeScope(self.attrs, **config_options))
        )

    def add_exception_handlers(self, exc_handlers: Sequence):
        """Add multiple exception handlers to the region.

        Args:
            exc_handlers (Sequence): Sequence (list, tuple) of handlers to be
                registered for the region. Each handler is defined by a tuple:
                `(exc_type: type, exc_handler: Callable, [config_options: dict])`
                For a detailed description of each, see `add_exception_handler`
                method documentation.
        """
        for exc_type, exc_handler, *config_options in exc_handlers:
            self.add_exception_handler(exc_type, exc_handler,
                                       **(config_options or {}))

    # Shortcut decorators - for defining exception handlers

    def exception(self, exc_type: type, **config_options):
        """Shortcut decorator for `add_exception_handler`.

        For detailed arguments description, see `add_exception_handler`
        documentation.

        Args:
            exc_type (type): Type of exceptions this handler should handle
            **config_options: Optional configuration parameters for the handler
        """
        def _decorator(func):
            self.add_exception_handler(exc_type, func)
            return func
        return _decorator

    def __repr__(self):
        return '<%s %s: %s %s>' % (self.__class__.__name__, self.name,
                                   self.endpoints, [r.name for r in self.regions])

class UrlRegion(BaseRegion):
    """UrlRegion groups endpoints in an app section with a common URL prefix.

    Endpoints belonging to the same UrlRegion share a common URL prefix
    (potentially with variable URL sections), as well as other configuration
    parameters. For more info about configuration parameters, see `BaseRegion`
    documentation.

    Attributes:
        name (str): The name of the app region
        regions (list): List of all subregions added to this region
        routes (list): List of all routes belonging to the region
        attrs (AttributeScope): Dictionary-like object containing all
    """

    def __init__(self, name: str, regions: Sequence=None, routes: Sequence=None,
                 **config_params):
        """UrlRegion object constructor.

        Constructs an app region identified by its `name`, optionally registeres
        provided routes and exception handlers, and stores given configuration
        parameters.

        Args:
            name (str): The name of the app region
            regions (optional, Sequence): A sequence of regions to be added to
                this region as its subregions
            routes (optional, Sequence): A sequence of routes to be added to
                this region (a shorthand definition). Each route is defined as
                a tuple:
                   `(url_rule, endpoint, [methods: list], [name: str], [params: dict])`
            **config_params: Optional configuration parameters shared between
                all routes belonging to this region
        """
        super().__init__(name, **config_params)

        if regions is not None:
            self.add_regions(regions)

        if routes is not None:
            self.add_routes(routes)

    def add_region(self, region, url_prefix: str=None):
        """Add a subregion to the app region.

        Adds an existing region as a subregion to this one. The subregion will
        inherit all configuration parameters of this region (but it can override
        them if desired).

        Args:
            region (Region): Existing app region to be added as a subregion
        """
        region.attrs.parent = self.attrs
        self.regions.append((region, url_prefix))

    def add_regions(self, regions: Sequence):
        """Add multiple subregions to the app region.

        For more details, see documentation of `add_region` method.

        Args:
            regions (Sequence): A sequence (list, tuple) of regions to be added
                to this region as subregions
        """
        for region, *url_prefix in regions:
            self.add_region(region, url_prefix)

    def add_route(self, url_rule: str, endpoint: Callable, **config_params):
        """Add a route to the app region.

        Registers a route to the region at a specified URL (potentially
        parametrized), which will respond to all requests having any of
        provided `methods` (if not set, default: GET).
        It also allows setting route specific configuration parameters via
        keyword-only arguments.

        URL rules support parametrized URL sections defined as
        `../{param_name:param_type}/..` (e.g. '/users/{id:int}'), with
        `param_type` being one of the following:
            - string - any text without a slash (the default type)
            - int - any (unsigned) integer
            - float - any floating-point number
            - path - any text, can include slashes

        The callable's parameters should be tagged with Python type hints to
        enable parameter type deduction and validation (otherwise, all
        parameters will be considered to be strings). Alternatively, a special
        decorator can be used to manually set parameter types and constraints
        (TODO: Route param decorator)


            methods (optional, Sequence): A sequence of uppercase strings
                listing all HTTP methods this endpoint will support (possible
                element values: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
            name (optional, str): A custom name assigned to this route
                (by default, it is the endpoint function/method name)

        Args:
            url_rule (str): An URL rule defining the URL paths for which this
                endpoint will receive requests
            endpoint (Callable): Any Python callable (a function, method,
                custom callable object...) which will be called to process
                requests for a given route.
            **config_params: Optional configuration parameters for this endpoint

        Raises:
            TODO: xyz - Invalid route definition?
        """
        self.endpoints.append((url_rule, endpoint, config_params))

    def add_routes(self, routes: Sequence):
        """Add multiple routes to the app region.

        Description of each route should contain at least the URL rule and the
        endpoint for the route, and optionally also the list of supported
        methods (by default only GET is supported), route name (by default the
        endpoint function/method name), and a dictionary containing route
        configuration parameters. For more info on expected URL rule format,
        as well as other parameters, see documentation for `add_route` method.

        Args:
            routes (Sequence): A sequence (list, tuple) of routes to be added to
                the region. Each route should be defined as a tuple:
                    `(url_rule, endpoint, [config_options: dict])`

        Raises:
            TODO: Invalid route definition?
        """
        for route_def in routes:
            if not isinstance(route_def, tuple):
                raise TypeError('Route definition should be a tuple: %s.' % route_def)

            if len(route_def) < 2:
                raise ValueError('Incorrect route definition (should contain at least'
                                 'the URL and endpoint): %s' % route_def)

            url_rule = route_def[0]
            endpoint = route_def[1]
            attrs = route_def[2] if len(route_def) > 2 else None

            # TODO: Except potential errors and notify which route caused it
            self.add_route(url_rule, endpoint, **(attrs or {}))

    # Shortcut decorators - for defining routes

    def route(self, url_rule: str, **config_params):
        """Shortcut decorator for `add_route` method.

        For detailed arguments description, see `add_route` documentation.

        Args:
            url_rule (str): An URL rule defining the URL paths for which this
                endpoint will receive requests
            **config_params: Optional configuration parameters for this endpoint
        Raises:
            TODO: Invalid route definition?
        """
        def _decorator(func):
            self.add_route(url_rule, func, **config_params)
            return func
        return _decorator

    def get(self, url_rule: str, **config_params):
        """Shortcut decorator for `add_route(..., methods=['GET'], ...)`.

        For detailed arguments description, see `add_route` documentation.

        Args:
            url_rule (str): An URL rule defining the URL paths for which this
                endpoint will receive requests
            **config_params: Optional configuration parameters for this endpoint
        Raises:
            TODO: Invalid route definition?
        """
        def _decorator(func):
            self.add_route(url_rule, func, methods=['GET'], **config_params)
            return func
        return _decorator

    def post(self, url_rule: str, **config_params):
        """Shortcut decorator for `add_route(..., methods=['POST'], ...)`.

        For detailed arguments description, see `add_route` documentation.

        Args:
            url_rule (str): An URL rule defining the URL paths for which this
                endpoint will receive requests
            **config_params: Optional configuration parameters for this endpoint
        Raises:
            TODO: Invalid route definition?
        """
        def _decorator(func):
            self.add_route(url_rule, func, methods=['POST'], **config_params)
            return func
        return _decorator

    def put(self, url_rule: str, **config_params):
        """Shortcut decorator for `add_route(..., methods=['PUT'], ...)`.

        For detailed arguments description, see `add_route` documentation.

        Args:
            url_rule (str): An URL rule defining the URL paths for which this
                endpoint will receive requests
            **config_params: Optional configuration parameters for this endpoint
        Raises:
            TODO: Invalid route definition?
        """
        def _decorator(func):
            self.add_route(url_rule, func, methods=['PUT'], **config_params)
            return func
        return _decorator

    def delete(self, url_rule: str, **config_params):
        """Shortcut decorator for `add_route(..., methods=['DELETE'], ...)`.

        For detailed arguments description, see `add_route` documentation.

        Args:
            url_rule (str): An URL rule defining the URL paths for which this
                endpoint will receive requests
            **config_params: Optional configuration parameters for this endpoint
        Raises:
            TODO: Invalid route definition?
        """
        def _decorator(func):
            self.add_route(url_rule, func, methods=['DELETE'], **config_params)
            return func
        return _decorator
