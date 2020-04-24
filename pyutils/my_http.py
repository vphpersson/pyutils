from __future__ import annotations
from abc import ABC
from typing import Dict, Type, Union
from http import HTTPStatus


def status_ok(status_code: int) -> bool:
    return 200 <= status_code <= 299


class HTTPStatusError(Exception, ABC):
    REASON_PHRASE: str = NotImplemented
    STATUS_CODE: int = NotImplemented

    STATUS_CODE_TO_CLASS: Dict[int, Type[HTTPStatusError]] = NotImplemented

    def __init__(self, response=None):
        super().__init__(f'{self.STATUS_CODE} {self.REASON_PHRASE}')
        self.response = response

    @classmethod
    def from_status_code(cls, status_code: Union[int, HTTPStatus], response=None) -> HTTPStatusError:
        return cls.STATUS_CODE_TO_CLASS[int(status_code)](response=response)


class HTTPClientStatusError(HTTPStatusError, ABC):
    pass


class HTTPServerStatusError(HTTPStatusError, ABC):
    pass


class BadRequestError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Bad Request'
    STATUS_CODE: int = 400


class UnauthorizedError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Unauthorized (RFC 7235)'
    STATUS_CODE: int = 401


class PaymentRequiredError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Payment Required'
    STATUS_CODE: int = 402


class ForbiddenError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Forbidden'
    STATUS_CODE: int = 403


class NotFoundError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Not Found'
    STATUS_CODE: int = 404


class MethodNotAllowedError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Method Not Allowed'
    STATUS_CODE: int = 405


class NotAcceptableError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Not Acceptable'
    STATUS_CODE: int = 406


class ProxyAuthenticationRequiredError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Proxy Authentication Required (RFC 7235)'
    STATUS_CODE: int = 407


class RequestTimeoutError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Request Timeout'
    STATUS_CODE: int = 408


class ConflictError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Conflict'
    STATUS_CODE: int = 409


class GoneError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Gone'
    STATUS_CODE: int = 410


class LengthRequiredError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Length Required'
    STATUS_CODE: int = 411


class PreconditionFailedError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Precondition Failed (RFC 7232)'
    STATUS_CODE: int = 412


class PayloadTooLargeError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Payload Too Large (RFC 7231)'
    STATUS_CODE: int = 413


class URITooLongError(HTTPClientStatusError):
    REASON_PHRASE: str = 'URI Too Long (RFC 7231)'
    STATUS_CODE: int = 414


class UnsupportedMediaTypeError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Unsupported Media Type (RFC 7231)'
    STATUS_CODE: int = 415


class RangeNotSatisfiableError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Range Not Satisfiable (RFC 7233)'
    STATUS_CODE: int = 416


class ExpectationFailedError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Expectation Failed'
    STATUS_CODE: int = 417


class ImATeapotError(HTTPClientStatusError):
    REASON_PHRASE: str = "I'm a teapot (RFC 2324, RFC 7168)"
    STATUS_CODE: int = 418


class MisdirectedRequestError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Misdirected Request (RFC 7540)'
    STATUS_CODE: int = 421


class UnprocessableEntityError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Unprocessable Entity (WebDAV; RFC 4918)'
    STATUS_CODE: int = 422


class LockedError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Locked (WebDAV; RFC 4918)'
    STATUS_CODE: int = 423


class FailedDependencyError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Failed Dependency (WebDAV; RFC 4918)'
    STATUS_CODE: int = 424


class TooEarlyError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Too Early (RFC 8470)'
    STATUS_CODE: int = 425


class UpgradeRequiredError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Upgrade Required'
    STATUS_CODE: int = 426


class PreconditionRequiredError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Precondition Required (RFC 6585)'
    STATUS_CODE: int = 428


class TooManyRequestsError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Too Many Requests (RFC 6585)'
    STATUS_CODE: int = 429


class RequestHeaderFieldsTooLargeError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Request Header Fields Too Large (RFC 6585)'
    STATUS_CODE: int = 431


class UnavailableForLegalReasonsError(HTTPClientStatusError):
    REASON_PHRASE: str = 'Unavailable For Legal Reasons (RFC 7725)'
    STATUS_CODE: int = 451


class InternalServerErrorError(HTTPServerStatusError):
    REASON_PHRASE: str = 'Internal Server Error'
    STATUS_CODE: int = 500


class NotImplementedStatusError(HTTPServerStatusError):
    REASON_PHRASE: str = 'Not Implemented'
    STATUS_CODE: int = 501


class BadGatewayError(HTTPServerStatusError):
    REASON_PHRASE: str = 'Bad Gateway'
    STATUS_CODE: int = 502


class ServiceUnavailableError(HTTPServerStatusError):
    REASON_PHRASE: str = 'Service Unavailable'
    STATUS_CODE: int = 503


class GatewayTimeoutError(HTTPServerStatusError):
    REASON_PHRASE: str = 'Gateway Timeout'
    STATUS_CODE: int = 504


class HTTPVersionNotSupportedError(HTTPServerStatusError):
    REASON_PHRASE: str = 'HTTP Version Not Supported'
    STATUS_CODE: int = 505


class VariantAlsoNegotiatesError(HTTPServerStatusError):
    REASON_PHRASE: str = 'Variant Also Negotiates (RFC 2295)'
    STATUS_CODE: int = 506


class InsufficientStorageError(HTTPServerStatusError):
    REASON_PHRASE: str = 'Insufficient Storage (WebDAV; RFC 4918)'
    STATUS_CODE: int = 507


class LoopDetectedError(HTTPServerStatusError):
    REASON_PHRASE: str = 'Loop Detected (WebDAV; RFC 5842)'
    STATUS_CODE: int = 508


class NotExtendedError(HTTPServerStatusError):
    REASON_PHRASE: str = 'Not Extended (RFC 2774)'
    STATUS_CODE: int = 510


class NetworkAuthenticationRequiredError(HTTPServerStatusError):
    REASON_PHRASE: str = 'Network Authentication Required (RFC 6585)'
    STATUS_CODE: int = 511


HTTPStatusError.STATUS_CODE_TO_CLASS = {
    400: BadRequestError,
    401: UnauthorizedError,
    402: PaymentRequiredError,
    403: ForbiddenError,
    404: NotFoundError,
    405: MethodNotAllowedError,
    406: NotAcceptableError,
    407: ProxyAuthenticationRequiredError,
    408: RequestTimeoutError,
    409: ConflictError,
    410: GoneError,
    411: LengthRequiredError,
    412: PreconditionFailedError,
    413: PayloadTooLargeError,
    414: URITooLongError,
    415: UnsupportedMediaTypeError,
    416: RangeNotSatisfiableError,
    417: ExpectationFailedError,
    418: ImATeapotError,
    421: MisdirectedRequestError,
    422: UnprocessableEntityError,
    423: LockedError,
    424: FailedDependencyError,
    425: TooEarlyError,
    426: UpgradeRequiredError,
    428: PreconditionRequiredError,
    429: TooManyRequestsError,
    431: RequestHeaderFieldsTooLargeError,
    451: UnavailableForLegalReasonsError,
    500: InternalServerErrorError,
    501: NotImplementedStatusError,
    502: BadGatewayError,
    503: ServiceUnavailableError,
    504: GatewayTimeoutError,
    505: HTTPVersionNotSupportedError,
    506: VariantAlsoNegotiatesError,
    507: InsufficientStorageError,
    508: LoopDetectedError,
    510: NotExtendedError,
    511: NetworkAuthenticationRequiredError
}
