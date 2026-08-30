from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from popquant.exec_math.types import Inventory, Side


@dataclass
class ReserveConfig:
    gamma: float = 0.1
    sigma2: float = 0.04
    tau: float = 1.0
    half_spread: float = 0.01
    max_abs_net: float = 50.0
    max_gross: float = 200.0


def reservation_price(
    mid: float,
    inv: Inventory,
    cfg: ReserveConfig,
) -> float:
    """
    r = m - q * γ * σ² * τ
    q = inv.net
    """
    if not (0.0 < mid < 1.0):
        mid = min(0.99, max(0.01, mid))
    r = mid - inv.net * cfg.gamma * cfg.sigma2 * cfg.tau
    return min(0.99, max(0.01, r))


def quote_ladder(r: float, cfg: ReserveConfig) -> dict:
    return {
        "bid_yes": max(0.01, r - cfg.half_spread),
        "ask_yes": min(0.99, r + cfg.half_spread),
        "bid_no": max(0.01, (1.0 - r) - cfg.half_spread),
        "ask_no": min(0.99, (1.0 - r) + cfg.half_spread),
    }


class LegCircuit:
    """Circuit breaker: planned two-leg arb, only one leg filled -> directional mode."""

    def __init__(self) -> None:
        self.pending_arb: Optional[str] = None
        self.filled_side: Optional[Side] = None
        self.open: bool = False

    def on_arb_submit(self, arb_id: str) -> None:
        self.pending_arb = arb_id
        self.filled_side = None
        self.open = True

    def on_fill(self, arb_id: str, side: Side) -> str:
        if not self.open or arb_id != self.pending_arb:
            return "ignore"
        if self.filled_side is None:
            self.filled_side = side
            return "one_leg"
        if self.filled_side != side:
            self.open = False
            return "complete"
        return "same_side_add"

    def allow_arb_add(self) -> bool:
        return (not self.open) or (self.filled_side is None)


def inventory_ok(inv: Inventory, cfg: ReserveConfig) -> bool:
    return abs(inv.net) <= cfg.max_abs_net and inv.gross <= cfg.max_gross
