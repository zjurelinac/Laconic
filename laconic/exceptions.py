"""Laconic framework exceptions

This module defines all default Laconic exceptions that might occur during
runtime of Laconic applications.

Exceptions:

    (HTTP errors:)

    BaseHTTPException (4xx-5xx)

    BaseClientError (4xx)
    BaseServerError (5xx)

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
    NotImplementedError (501)
    BadGatewayError (502)
    ServiceUnavailableError (503)
    GatewayTimeoutError (504)
    HTTPUnsupportedVersionError (505)

    (Custom:)

    InvalidParameterError (400)
    MissingParameterError (400)
    EndpointNotFoundError (404)

    ContextProcessingError (500)
    EndpointRuntimeError (500)

    (Non-HTTP:)

    EndpointDefinitionError

Copyright:  (c) Zvonimir Jurelinac 2018
License:    MIT, see LICENSE for more details
"""


