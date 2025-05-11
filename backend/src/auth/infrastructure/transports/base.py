import abc

from starlette.requests import Request
from starlette.responses import Response


class IAuthTransport(abc.ABC):
    """
    Interface for token transports strategies.

    Defines how tokens are extracted from and injected into HTTP responses/requests,
    e.g., via cookies or headers.
    """

    @abc.abstractmethod
    def set_token(self, response: Response, token: str) -> None:
        """
        Set the token in the response.

        :param response: The outgoing HTTP response.
        :param token: The token to be set.
        """
        pass

    @abc.abstractmethod
    def delete_token(self, response: Response) -> None:
        """
        Remove the token from the response.

        :param response: The outgoing HTTP response.
        """
        pass

    @abc.abstractmethod
    def get_token(self, request: Request) -> str | None:
        """
        Extract the token from the request.

        :param request: The incoming HTTP request.
        :return: Extracted token or None.
        """
        pass
