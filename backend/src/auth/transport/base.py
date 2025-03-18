from typing import Protocol

from fastapi.security.base import SecurityBase


class Transport(Protocol):
    scheme: SecurityBase
