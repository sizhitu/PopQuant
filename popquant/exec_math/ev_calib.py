from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from popquant.exec_math.types import FillLog, Intent, Side


def net_ev(intent: Intent) -> float:
    """
    Buy YES: EV = π̂ - p - c
    Buy NO:  flip π̂, p to 1-π̂, 1-p
    """
    p, pi = intent.p_mkt, intent.pi_hat
    c = intent.fee_per_share + intent.slip
    if intent.side == Side.NO:
        p, pi = 1.0 - p, 1.0 - pi
    return pi - p - c


def size_fractional_kelly(
    intent: Intent,
    bankroll: float,
    fraction: float = 0.25,
    cap_frac: float = 0.02,
) -> float:
    ev = net_ev(intent)
    if ev <= 0 or bankroll <= 0:
        return 0.0
    p = intent.p_mkt if intent.side == Side.YES else 1.0 - intent.p_mkt
    f_star = ev / max(1e-6, 1.0 - p)
    f = min(f_star * fraction, cap_frac)
    return max(0.0, f * bankroll / max(1e-6, intent.p_mkt))


@dataclass
class CalibrationBook:
    bins: int = 10
    rows: list[FillLog] = field(default_factory=list)

    def add(self, row: FillLog) -> None:
        required = (
            row.market_id,
            row.side,
            row.pi_hat,
            row.p_exec,
            row.qty,
            row.fees,
            row.ts_open,
        )
        if any(x is None for x in required):
            raise ValueError("FillLog missing required fields")
        if not (0.0 <= row.pi_hat <= 1.0):
            raise ValueError("pi_hat out of range")
        self.rows.append(row)

    def reliability(self) -> list[dict]:
        buckets: list[list[FillLog]] = [[] for _ in range(self.bins)]
        for r in self.rows:
            if r.resolved is None:
                continue
            i = min(self.bins - 1, int(r.pi_hat * self.bins))
            i = max(0, i)
            buckets[i].append(r)
        out: list[dict] = []
        for i, rs in enumerate(buckets):
            if not rs:
                continue
            out.append(
                {
                    "bin": i,
                    "n": len(rs),
                    "pi_mean": sum(x.pi_hat for x in rs) / len(rs),
                    "freq": sum(1 for x in rs if x.resolved) / len(rs),
                }
            )
        return out
