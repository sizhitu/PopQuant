import time

import pytest

from popquant.exec_math.types import FillLog, Intent, Side
from popquant.exec_math.ev_calib import CalibrationBook, net_ev, size_fractional_kelly


def _intent(side, p, pi, fee=0.0, slip=0.0):
    return Intent(
        side=side,
        p_mkt=p,
        pi_hat=pi,
        qty=1.0,
        fee_per_share=fee,
        slip=slip,
        ts=time.time(),
        market_id="m1",
        tag="directional",
    )


def test_v1_positive_ev():
    # π̂=0.6, p=0.5, c=0.02 -> EV=0.08
    it = _intent(Side.YES, 0.5, 0.6, fee=0.02)
    assert abs(net_ev(it) - 0.08) < 1e-12


def test_v2_high_winrate_negative_ev_zero_size():
    # π̂=0.9, p=0.92, c=0.01 -> EV=-0.03
    it = _intent(Side.YES, 0.92, 0.9, fee=0.01)
    assert net_ev(it) < 0
    assert size_fractional_kelly(it, bankroll=10_000) == 0.0


def test_v3_position_capped():
    it = _intent(Side.YES, 0.5, 0.7, fee=0.01)
    bankroll = 10_000.0
    qty = size_fractional_kelly(it, bankroll, fraction=0.25, cap_frac=0.02)
    # notional upper bound ~ cap_frac * bankroll
    notional = qty * it.p_mkt
    assert notional <= bankroll * 0.02 + 1e-6
    assert qty > 0


def test_v4_reliability_detects_miscalibration():
    book = CalibrationBook(bins=10)
    # bin for 0.50-0.60: many logs with pi_hat~0.55 but low realized freq
    for i in range(100):
        book.add(
            FillLog(
                market_id=f"m{i}",
                side=Side.YES,
                pi_hat=0.55,
                p_exec=0.50,
                qty=1.0,
                fees=0.0,
                resolved=(i < 40),  # 40% realized
                ts_open=float(i),
                ts_resolve=float(i + 1),
            )
        )
    rel = book.reliability()
    assert len(rel) >= 1
    row = rel[0]
    assert row["n"] == 100
    assert abs(row["pi_mean"] - 0.55) < 1e-9
    assert abs(row["freq"] - 0.40) < 1e-9
    assert row["freq"] < row["pi_mean"] - 0.05  # miscalibrated


def test_v5_missing_fields_rejected():
    book = CalibrationBook()
    with pytest.raises(ValueError):
        book.add(
            FillLog(
                market_id="",
                side=Side.YES,
                pi_hat=0.5,
                p_exec=0.5,
                qty=1.0,
                fees=0.0,
                resolved=None,
                ts_open=None,  # type: ignore
                ts_resolve=None,
            )
        )
