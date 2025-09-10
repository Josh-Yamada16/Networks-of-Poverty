from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    MONEY = auto()
    TRUST = auto()
    VOUCHER = auto()

@dataclass
class Token:
    name: str | None
    token_type: TokenType
    value: float | None
    issuer: str | None
