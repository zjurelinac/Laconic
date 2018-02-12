"""
App regions.

This module defines the abstract concept of an app region as a group of related
endpoints forming a distinct part of the app. It also provides a specific
implementation of a URLRegion, which represents a group of endpoints sharing a
common URL prefix.

Classes:
    BaseRegion - Abstract app region class
    UrlRegion - URL-identified app region
    RpcRegion - ...

Todos:
    TODO: RpcRegion

Copyright:  (c) Zvonimir Jurelinac 2018
License:    MIT, see LICENSE for more details
"""

from collections.abc import Callable, Sequence

from .exceptions import EndpointDefinitionError, EndpointDefinitionWarning
from .routing import Endpoint
from .util import AttributeScope, Dispatchable, ExceptionHandler

class BaseRegion:
    """BaseRegion object groups a set of related endpoints in a single whole.

    A base class for more specific app region implementations. Provides means
    for defining region-specific configuration parameters (which will then apply
    to all contained endpoints, handlers and subregions, unless overriden) and
    exception handlers.

    Attributes:
        name (str): The name of the app region
        endpoints (list): List of all endpoints belonging to this region
        regions (list): List of all subregions added to this region
        region_attrs (AttributeScope): Dictionary-like object containing
            region-specific configuration parameters
    """

    __slots__ = ['name', 'endpoints', 'regions', 'region_attrs']

    def __init__(self, name: str, endpoints: Sequence=None,
                 regions: Sequence=None, **region_attrs):
        """BaseRegion object constructor.

        Constructs an app region identified by its `name`, registers all
        provided endpoints and subregions, and stores all passed configuration
        parameters. Available endpoint configuration parameters common to all
        types of regions are:
            exception_handlers (List[Exception, Callable]): List of handlers for
                particular exception types
            before_request (List[Callable]): List of hooks to be executed before
                each request directed to this app region. Hooks will be executed
                in order they were listed, and
            after_request (List[Callable]): List of hooks to be executed after
                each request directed to this app region

        Args:
            name (str): Name of the app region
            regions (optional, Sequence): A sequence of regions to be added to
                this region as its subregions
            endpoints (optional, Sequence): A sequence of endpoints to be added
                to this region (a shorthand definition).
                Each endpoint is defined as a tuple:
                    `(endpoint, [endpoint_params: dict])`
            **region_attrs: Optional configuration parameters for this region
        """
        self.name = name
        self.endpoints = []
        self.regions = []
        self.region_attrs = AttributeScope(**region_attrs)

        if endpoints is not None:
            self.add_endpoints(endpoints)

        if regions is not None:
            self.add_regions(regions)

        if 'exception_handlers' not in self.region_attrs:
            self.region_attrs['exception_handlers'] = []

        if 'before_request' not in self.region_attrs:
            self.region_attrs['before_request'] = []

        if 'after_request' not in self.region_attrs:
            self.region_attrs['after_request'] = []

    def add_endpoint(self, endpoint: Callable, **endpoint_attrs):
        """Add an endpoint to the app region.

        Registers an endpoint to the region, also allowing to set
        endpoint-specific configuration parameters via keyword-only arguments.

        The endpoint callable's parameters should be tagged with Python type
        hints to enable parameter type deduction and validation (otherwise, all
        parameters will be considered to be strings).

        Args:
            endpoint (Callable): Any Python callable (a function, method,
                custom callable object...) which will be called to process
                requests for a given route.
            **endpoint_attrs: Optional configuration parameters for this endpoint
        """
        self.endpoints.append(
            (endpoint, AttributeScope(self.region_attrs, **endpoint_attrs))
        )

    def add_endpoints(self, endpoints: Sequence):
        """Add multiple endpoints to the app region.

        Description of each endpoint should contain the callable for the
        endpoint, and optionally a dictionary containing endpoint
        configuration parameters. For more info, see documentation for
        `add_endpoint` method.

        Args:
            endpoints (Sequence): A sequence (list, tuple) of endpoints to be
                added to the region. Each endpoint should be defined as a tuple:
                    `(endpoint, [endpoint_attrs: dict])`
        """
        for endpoint, *endpoint_attrs in endpoints:
            self.add_endpoint(endpoint, **(endpoint_attrs or {}))

    def add_region(self, region):
        """Add a subregion to the app region.

        Adds an existing region as a subregion to this one. The subregion will
        inherit all configuration parameters of this region (but it can override
        them if desired).

        Args:
            region (Region): Existing app region to be added as a subregion
        """
        region.region_attrs.parent = self.region_attrs
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
                              **handler_attrs):
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
            **handler_attrs: Optional configuration parameters for the handler
        """
        self.region_attrs['exception_handlers'].append(
            ExceptionHandler(exc_type, exc_handler,
                             AttributeScope(self.region_attrs, **handler_attrs))
        )

    def add_exception_handlers(self, exc_handlers: Sequence):
        """Add multiple exception handlers to the region.

        Args:
            exc_handlers (Sequence): Sequence (list, tuple) of handlers to be
                registered for the region. Each handler is defined by a tuple:
                `(exc_type: type, exc_handler: Callable, [handler_attrs: dict])`
                For a detailed description of each, see `add_exception_handler`
                method documentation.
        """
        for exc_type, exc_handler, *handler_attrs in exc_handlers:
            self.add_exception_handler(exc_type, exc_handler,
                                       **(handler_attrs or {}))

    # Shortcut decorators - for defining exception handlers

    def exception(self, exc_type: type, **handler_attrs):
        """Shortcut decorator for `add_exception_handler`.

        For detailed arguments description, see `add_exception_handler`
        documentation.

        Args:
            exc_type (type): Type of exceptions this handler should handle
            **handler_attrs: Optional configuration parameters for the handler
        """
        def _decorator(func):
            self.add_exception_handler(exc_type, func, **handler_attrs)
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
        endpoints (list): List of all endpoints belonging to the region
        regions (list): List of all subregions added to this region
        region_attrs (AttributeScope): Dictionary-like object containing
            region-specific configuration parameters
    """

    def __init__(self, name: str, endpoints: Sequence=None,
                 regions: Sequence=None, **region_attrs):
        """UrlRegion object constructor.

        Constructs an app region identified by its `name`, optionally registeres
        provided endpoints and exception handlers, and stores given configuration
        parameters.

        Args:
            name (str): The name of the app region
            regions (optional, Sequence): A sequence of regions to be added to
                this region as its subregions
            endpoints (optional, Sequence): A sequence of endpoints to be added
                to this region (a shorthand definition).
                Each endpoint is defined as a tuple:
                   `(url_rule, endpoint, [endpoint_params: dict])`
            **region_attrs: Optional configuration parameters for this region
        """
        super().__init__(name, endpoints, regions, **region_attrs)

    def add_region(self, region, url_prefix: str=None):
        """Add a subregion to the app region.

        Adds an existing region as a subregion to this one. The subregion will
        inherit all configuration parameters of this region (but it can override
        them if desired).

        Args:
            region (Region): Existing app region to be added as a subregion
        """
        region.region_attrs.parent = self.region_attrs
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

    def add_endpoint(self, url_rule: str, endpoint: Callable, **endpoint_attrs):
        """Add an endpoint to the app region.

        Registers an endpoint to the region at a specified URL (potentially
        parametrized), which will respond to all requests having any of
        provided `methods` (if not set, default: GET).
        It also allows setting endpoint-specific configuration parameters via
        keyword-only arguments.

        URL rules support parametrized URL sections defined as
        `../{param_name:param_type}/..` (e.g. '/users/{id:int}'), with
        `param_type` being one of the following:
            - string - any text without a slash (the default type)
            - int - any (unsigned) integer
            - float - any floating-point number
            - path - any text, can include slashes

        The endpoint callable's parameters should be tagged with Python type
        hints to enable parameter type deduction and validation (otherwise, all
        parameters will be considered to be strings).

        Args:
            url_rule (str): An URL rule defining the URL paths for which this
                endpoint will receive requests
            endpoint (Callable): Any Python callable (a function, method,
                custom callable object...) which will be called to process
                requests for a given route.
            **endpoint_attrs: Optional configuration parameters for this endpoint
        """
        self.endpoints.append(
            (url_rule, endpoint, AttributeScope(self.region_attrs, **endpoint_attrs))
        )

    def add_endpoints(self, endpoints: Sequence):
        """Add multiple endpoints to the app region.

        Description of each endpoint should contain at least the URL rule and
        the callable for the endpoint, and optionally also the list of supported
        methods (by default only GET is supported), endpoint name (by default
        the endpoint function/method name), and a dictionary containing endpoint
        configuration parameters. For more info on expected URL rule format,
        as well as other parameters, see documentation for `add_endpoint` method.

        Args:
            endpoints (Sequence): A sequence (list, tuple) of endpoints to be
                added to the region. Each endpoint should be defined as a tuple:
                    `(url_rule, endpoint, [endpoint_attrs: dict])`
        """
        for url_rule, endpoint, *endpoint_attrs in endpoints:
            self.add_endpoint(url_rule, endpoint, **(endpoint_attrs or {}))

    # Shortcut decorators - for defining routes

    def endpoint(self, url_rule: str, **endpoint_attrs):
        """Shortcut decorator for `add_endpoint` method.

        For detailed arguments description, see `add_route` documentation.

        Args:
            url_rule (str): An URL rule defining the URL paths for which this
                endpoint will receive requests
            **endpoint_attrs: Optional configuration parameters for this endpoint
        """
        def _decorator(func):
            self.add_endpoint(url_rule, func, **endpoint_attrs)
            return func
        return _decorator

    def get(self, url_rule: str, **endpoint_attrs):
        """Shortcut decorator for `add_endpoint(..., methods=['GET'], ...)`.

        For detailed arguments description, see `add_endpoint` documentation.

        Args:
            url_rule (str): An URL rule defining the URL paths for which this
                endpoint will receive requests
            **endpoint_attrs: Optional configuration parameters for this endpoint
        """
        def _decorator(func):
            self.add_endpoint(url_rule, func, methods=['GET'], **endpoint_attrs)
            return func
        return _decorator

    def post(self, url_rule: str, **endpoint_attrs):
        """Shortcut decorator for `add_endpoint(..., methods=['POST'], ...)`.

        For detailed arguments description, see `add_endpoint` documentation.

        Args:
            url_rule (str): An URL rule defining the URL paths for which this
                endpoint will receive requests
            **endpoint_attrs: Optional configuration parameters for this endpoint
        """
        def _decorator(func):
            self.add_endpoint(url_rule, func, methods=['POST'], **endpoint_attrs)
            return func
        return _decorator

    def put(self, url_rule: str, **endpoint_attrs):
        """Shortcut decorator for `add_endpoint(..., methods=['PUT'], ...)`.

        For detailed arguments description, see `add_endpoint` documentation.

        Args:
            url_rule (str): An URL rule defining the URL paths for which this
                endpoint will receive requests
            **endpoint_attrs: Optional configuration parameters for this endpoint
        """
        def _decorator(func):
            self.add_endpoint(url_rule, func, methods=['PUT'], **endpoint_attrs)
            return func
        return _decorator

    def delete(self, url_rule: str, **endpoint_attrs):
        """Shortcut decorator for `add_endpoint(..., methods=['DELETE'], ...)`.

        For detailed arguments description, see `add_endpoint` documentation.

        Args:
            url_rule (str): An URL rule defining the URL paths for which this
                endpoint will receive requests
            **endpoint_attrs: Optional configuration parameters for this endpoint
        """
        def _decorator(func):
            self.add_endpoint(url_rule, func, methods=['DELETE'], **endpoint_attrs)
            return func
        return _decorator


class RpcRegion(BaseRegion):
    """"""
