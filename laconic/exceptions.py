"""Laconic framework exceptions

This module defines all default Laconic exceptions that might occur during
runtime of Laconic applications.

Exceptions:

    (HTTP exceptions:)

    BaseHTTPException (3xx-5xx)

    RedirectionException (3xx)
    BaseClientError (4xx)
    BaseServerError (5xx)

    MovedPermanentlyException (301)
    FoundException (302)
    SeeOtherException (303)
    NotModifiedException (304)
    UseProxyException (305)
    TemporaryRedirectException (307)
    PermanentRedirectException (308)

    BadRequestError (400)
    UnauthorizedError (401)
    PaymentRequiredError (402)
    ForbiddenError (403)
    NotFoundError (404)
    MethodNotAllowedError (405)
    NotAcceptableError (406)
    ProxyAuthRequiredError (407)
    RequestTimeoutError (408)
    ConflictError (409)
    GoneError (410)
    LengthRequiredError (411)
    PreconditionFailedError (412)
    PayloadTooLargeError (413)
    URITooLongError (414)
    UnsupportedMediaTypeError (415)
    RangeNotSatisfiableError (416)
    ExpectationFailedError (417)
    MisdirectedRequestError (421)
    UnprocessableEntityError (422)
    UpgradeRequiredError (426)
    PreconditionRequiredError (428)
    TooManyRequestsError (429)

    InternalServerError (500)
    EndpointNotImplementedError (501)
    BadGatewayError (502)
    ServiceUnavailableError (503)
    GatewayTimeoutError (504)
    UnsupportedHTTPVersionError (505)

    (Custom:)

    InvalidParameterError (400)
    MissingParameterError (400)
    EndpointNotFoundError (404)

    ContextProcessingError (500)
    EndpointRuntimeError (500)

    (Non-HTTP:)

    EndpointDefinitionError
    EndpointDefinitionWarning

Copyright:  (c) Zvonimir Jurelinac 2018
License:    MIT, see LICENSE for more details
"""


from .util import camel_case_split


class BaseHTTPException(Exception):
    """HTTP exception base class.

    Contains all required data to generate an HTTP response describing the
    exception to the user.

    Attributes:
        status_code (int): HTTP status code corresponding to the exception
        name (str): User-friendly error name
        description (str): User-friendly description of the error (default: None)
        headers (dict): Extra headers to add to the response generated from
            this exception
        data (any): Arbitrary additional data which can be provided with the
            exception (default: None)
        has_representation (bool): Whether exception generates a response body
    """

    __slots__ = ['status_code', 'name', 'description', 'headers', 'data',
                 'has_representation']

    def __init__(self, status_code, name=None, description=None, headers=None, data=None):
        self.status_code = status_code
        self.name = name or _exc_name_from_class(self.__class__)
        self.description = description
        self.headers = headers
        self.data = data

    def __repr__(self):
        return '<%s: %s (%d)>' % (self.__class__.__name__, self.description, self.status_code)


class RedirectionException(BaseHTTPException):
    """Base class for HTTP 3xx exceptions."""


class BaseClientError(BaseHTTPException):
    """Base class for HTTP 4xx exceptions."""


class BaseServerError(BaseHTTPException):
    """Base class for HTTP 4xx exceptions."""


# HTTP 3xx statuses

class MovedPermanentlyException(RedirectionException):
    """Resource has been moved permanently to the new URI"""
    def __init__(self, location, **kwargs):
        super().__init__(status_code=301, has_representation=False,
                         headers={'Location': location}, **kwargs)


class FoundException(RedirectionException):
    """Resource can be found on another URI."""
    def __init__(self, location, **kwargs):
        super().__init__(status_code=302,has_representation=False,
                         headers={'Location': location}, **kwargs)


class SeeOtherException(RedirectionException):
    """Response to this request can be found on another URI and obtained with GET."""
    def __init__(self, location, **kwargs):
        super().__init__(status_code=303, has_representation=False,
                         headers={'Location': location}, **kwargs)


class NotModifiedException(RedirectionException):
    """Requested resource has not been modified and needn't be retransmitted."""
    def __init__(self, **kwargs):
        super().__init__(status_code=304, has_representation=False, **kwargs)


class UseProxyException(RedirectionException):
    """The requested resource is available only through a proxy."""
    def __init__(self, location, **kwargs):
        super().__init__(status_code=305, has_representation=False,
                         headers={'Location': location}, **kwargs)


class TemporaryRedirectException(RedirectionException):
    """The request should be repeated with another URI, but future requests not."""
    def __init__(self, location, **kwargs):
        super().__init__(status_code=307, has_representation=False,
                         headers={'Location': location} **kwargs)


class PermanentRedirectException(RedirectionException):
    """This request and all future requests should be repeated with another URI."""
    def __init__(self, location, **kwargs):
        super().__init__(status_code=308, has_representation=False,
                         headers={'Location': location} **kwargs)


# HTTP 4xx statuses


class BadRequestError(BaseClientError):
    """Server can or will not process the request due to client error."""
    def __init__(self, **kwargs):
        super().__init__(status_code=400, **kwargs)


class UnauthorizedError(BaseClientError):
    """Authentication is required and has failed or has not been provided."""
    def __init__(self, **kwargs):
        super().__init__(status_code=401, **kwargs)


class PaymentRequiredError(BaseClientError):
    """Currently unused."""
    def __init__(self, **kwargs):
        super().__init__(status_code=402, **kwargs)


class ForbiddenError(BaseClientError):
    """The user does not have the necessary permissions for a resource."""
    def __init__(self, **kwargs):
        super().__init__(status_code=403, **kwargs)


class NotFoundError(BaseClientError):
    """The requested resource could not be found."""
    def __init__(self, **kwargs):
        super().__init__(status_code=404, **kwargs)


class MethodNotAllowedError(BaseClientError):
    """Request method is not supported for the requested resource."""
    def __init__(self, allowed_methods=None, **kwargs):
        data = kwargs.pop('data', {})
        data['allowed_methods'] = allowed_methods
        super().__init__(status_code=405, data=data, **kwargs)


class NotAcceptableError(BaseClientError):
    """The requested resource cannot generate any acceptable representation.
    
    Acceptable representations are defined in Accept request header.
    """
    def __init__(self, **kwargs):
        super().__init__(status_code=406, **kwargs)


class ProxyAuthRequiredError(BaseClientError):
    """The client must first authenticate itself with the proxy."""
    def __init__(self, **kwargs):
        super().__init__(status_code=407, **kwargs)


class RequestTimeoutError(BaseClientError):
    """Server timed out waiting for the request."""
    def __init__(self, **kwargs):
        super().__init__(status_code=408, **kwargs)


class ConflictError(BaseClientError):
    """The request could not be processed because of conflict in the request."""
    def __init__(self, **kwargs):
        super().__init__(status_code=409, **kwargs)


class GoneError(BaseClientError):
    """Resource requested is no longer available and won't be available again."""
    def __init__(self, **kwargs):
        super().__init__(status_code=410, **kwargs)


class LengthRequiredError(BaseClientError):
    """The request did not specify the length of its content."""
    def __init__(self, **kwargs):
        super().__init__(status_code=411, **kwargs)


class PreconditionFailedError(BaseClientError):
    """Server does not meet one of the requester's preconditions."""
    def __init__(self, **kwargs):
        super().__init__(status_code=412, **kwargs)


class PayloadTooLargeError(BaseClientError):
    """The request is larger than the server is willing or able to process."""
    def __init__(self, **kwargs):
        super().__init__(status_code=413, **kwargs)


class URITooLongError(BaseClientError):
    """The URI provided was too long for the server to process."""
    def __init__(self, **kwargs):
        super().__init__(status_code=414, **kwargs)


class UnsupportedMediaTypeError(BaseClientError):
    """Request entity's media type is unsupported by the server or resource."""
    def __init__(self, **kwargs):
        super().__init__(status_code=415, **kwargs)


class RangeNotSatisfiableError(BaseClientError):
    """Client has asked for a portion of the file the server can't supply."""
    def __init__(self, **kwargs):
        super().__init__(status_code=416, **kwargs)


class ExpectationFailedError(BaseClientError):
    """The server can't meet the requirements of the Expect request header."""
    def __init__(self, **kwargs):
        super().__init__(status_code=417, **kwargs)


class MisdirectedRequestError(BaseClientError):
    """Request was directed at a server that is unable to produce a response."""
    def __init__(self, **kwargs):
        super().__init__(status_code=421, **kwargs)


class UnprocessableEntityError(BaseClientError):
    """Request was well-formed but could not be followed due to semantic errors."""
    def __init__(self, **kwargs):
        super().__init__(status_code=422, **kwargs)


class UpgradeRequiredError(BaseClientError):
    """Client should switch to a different protocol given in the Upgrade header."""
    def __init__(self, **kwargs):
        super().__init__(status_code=426, **kwargs)


class PreconditionRequiredError(BaseClientError):
    """The origin server requires the request to be conditional."""
    def __init__(self, **kwargs):
        super().__init__(status_code=428, **kwargs)


class TooManyRequestsError(BaseClientError):
    """The user has sent too many requests in a given amount of time."""
    def __init__(self, **kwargs):
        super().__init__(status_code=429, **kwargs)


# HTTP 5xx statuses

class InternalServerError(BaseServerError):
    """An unexpected condition was encountered during processing of the request."""
    def __init__(self, **kwargs):
        super().__init__(status_code=500, **kwargs)


class EndpointNotImplementedError(BaseServerError):
    """Server does not recognize the request method or lacks the ability to fulfil the request."""
    def __init__(self, **kwargs):
        super().__init__(status_code=501, **kwargs)


class BadGatewayError(BaseServerError):
    """The server received invalid response from upstream server.
    
    (The server was acting as a gateway or proxy)
    """
    def __init__(self, **kwargs):
        super().__init__(status_code=502, **kwargs)


class ServiceUnavailableError(BaseServerError):
    """The server is currently unavailable (due to overload or maintenance)."""
    def __init__(self, **kwargs):
        super().__init__(status_code=503, **kwargs)


class GatewayTimeoutError(BaseServerError):
    """The server didn't receive a timely response from upstream server.
    
    (The server was acting as a gateway or proxy)
    """
    def __init__(self, **kwargs):
        super().__init__(status_code=504, **kwargs)


class UnsupportedHTTPVersionError(BaseServerError):
    """Server doesn'ot support the HTTP protocol version used in the request."""
    def __init__(self, **kwargs):
        super().__init__(status_code=505, **kwargs)


# Custom exceptions

class InvalidParameterError(BadRequestError):
    """Request parameter is malformed or invalid."""
    

class MissingParameterError(BadRequestError):
    """A required parameter is missing from the request."""
    

class EndpointNotFoundError(NotFoundError):
    """There is no endpoint available on this route."""
    

class ContextProcessingError(InternalServerError):
    """Wrapper for exceptions occurred during internal processing of the request."""


class EndpointRuntimeError(InternalServerError):
    """Wrapper for exceptions occurred during the execution of an endpoint."""


class EndpointDefinitionError(RuntimeError):
    """Endpoint or one of its parameters is incorrectly defined."""


class EndpointDefinitionWarning(UserWarning):
    """Some aspect of endpoint definition could be problematic and/or done better."""


# Utility functions

def _exc_name_from_class(cls):
    IGNORE = ['api', 'exception', 'error', 'warning']
    return ' '.join(w.capitalize() for w in camel_case_split(cls.__name__) if w.lower() not in IGNORE)
