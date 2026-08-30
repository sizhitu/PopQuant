from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Side(Enum):
    YES = "YES"
    NO = "NO"


@dataclass(frozen=True)
class Level:
    price: float  # [0, 1]
    size: float  # executable shares


@dataclass(frozen=True)
class Book:
    yes_asks: tuple[Level, ...]  # ascending price
    no_asks: tuple[Level, ...]
    yes_bids: tuple[Level, ...]  # descending price
    no_bids: tuple[Level, ...]
    ts: float


@dataclass(frozen=True)
class FeeModel:
    taker_bps: float
    maker_bps: float
    min_fee: float = 0.0


@dataclass
class Inventory:
    yes: float = 0.0
    no: float = 0.0

    @property
    def net(self) -> float:
        """Positive = long YES bias; negative = long NO bias."""
        return self.yes - self.no

    @property
    def gross(self) -> float:
        return self.yes + self.no


@dataclass(frozen=True)
class Intent:
    side: Side
    p_mkt: float
    pi_hat: float
    qty: float
    fee_per_share: float
    slip: float
    ts: float
    market_id: str
    tag: str  # "arb" | "inventory" | "directional"


@dataclass
class FillLog:
    market_id: str
    side: Side
    pi_hat: float
    p_exec: float
    qty: float
    fees: float
    resolved: Optional[bool]  # True if this side won
    ts_open: float
    ts_resolve: Optional[float]
