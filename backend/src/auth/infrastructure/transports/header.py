from starlette.requests import Request
from starlette.responses import Response

from src.auth.infrastructure.transports.base import IAuthTransport


class HeaderTransport(IAuthTransport):
    """
    Transport strategy using HTTP headers to manage tokens.
    """

    def __init__(
        self,
        header_name: str,
        token_type_prefix: str | None = None,
    ) -> None:
        """
        Initialize header transports.

        :param header_name: The name of the header to use (e.g., "Authorization").
        :param token_type_prefix: Optional prefix like "Bearer" to prepend to the token.
        """
        self.header_name = header_name
        self.token_type_prefix = token_type_prefix

    def set_token(self, response: Response, token: str) -> None:
        """
        Set the token in the specified header of the response.

        :param response: The outgoing HTTP response.
        :param token: The token to be set.
        """
        if self.token_type_prefix:
            token_value = f"{self.token_type_prefix} {token}"
        else:
            token_value = token
        response.headers[self.header_name] = token_value

    def delete_token(self, response: Response) -> None:
        """
        Remove the token from the response header.

        :param response: The outgoing HTTP response.
        """
        response.headers[self.header_name] = ""

    def get_token(self, request: Request) -> str | None:
        """
        Extract the token from the request header.

        :param request: The incoming HTTP request.
        :return: Token string or None.
        """
        header = request.headers.get(self.header_name, None)
        if header:
            try:
                return header.split(" ")[1]
            except IndexError:
                return header
