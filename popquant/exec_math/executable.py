from __future__ import annotations

from typing import Optional

from popquant.exec_math.types import Book, FeeModel, Level


def executable_cost(levels: tuple[Level, ...], qty: float) -> Optional[float]:
    """
    Walk the book from best to worst; return total cost to buy `qty`.
    Returns None if depth is insufficient.
    C(Q) = sum p_i * q_i
    """
    if qty <= 0:
        return 0.0
    remain, cost = qty, 0.0
    for lv in levels:
        if lv.price < 0 or lv.price > 1 or lv.size < 0:
            continue
        take = min(remain, lv.size)
        cost += take * lv.price
        remain -= take
        if remain <= 1e-12:
            return cost
    return None


def complementary_edge(
    book: Book,
    qty: float,
    fee: FeeModel,
    delta: float = 0.02,
) -> Optional[dict]:
    """
    Executable complement arb when per-share residual exceeds delta:
      1 - (C_yes(Q) + C_no(Q) + fees) / Q >= delta
    Q pairs pay out Q at resolution.
    """
    if qty <= 0:
        return None
    cy = executable_cost(book.yes_asks, qty)
    cn = executable_cost(book.no_asks, qty)
    if cy is None or cn is None:
        return None
    # Simplified: both legs treated as taker; production should split maker/taker.
    fees = qty * (fee.taker_bps / 1e4) * 2
    total_cost = cy + cn + fees
    vwap_yes = cy / qty
    vwap_no = cn / qty
    edge_per_share = 1.0 - (total_cost / qty)
    if edge_per_share < delta:
        return None
    return {
        "qty": qty,
        "cost_yes": cy,
        "cost_no": cn,
        "fees": fees,
        "total": total_cost,
        "edge": edge_per_share,
        "edge_total": qty - total_cost,
        "vwap_yes": vwap_yes,
        "vwap_no": vwap_no,
    }
