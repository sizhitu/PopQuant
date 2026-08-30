from popquant.exec_math.types import Inventory, Side
from popquant.exec_math.inventory import (
    LegCircuit,
    ReserveConfig,
    inventory_ok,
    quote_ladder,
    reservation_price,
)


def test_i1_zero_inventory():
    cfg = ReserveConfig()
    inv = Inventory(yes=0, no=0)
    r = reservation_price(0.5, inv, cfg)
    assert abs(r - 0.5) < 1e-12


def test_i2_long_yes_lowers_reserve():
    cfg = ReserveConfig(gamma=0.1, sigma2=0.04, tau=1.0)
    inv = Inventory(yes=20, no=0)
    r = reservation_price(0.5, inv, cfg)
    assert r < 0.5


def test_i3_one_leg_blocks_arb_add():
    c = LegCircuit()
    c.on_arb_submit("A")
    status = c.on_fill("A", Side.YES)
    assert status == "one_leg"
    assert c.allow_arb_add() is False


def test_i4_second_leg_completes():
    c = LegCircuit()
    c.on_arb_submit("A")
    c.on_fill("A", Side.YES)
    status = c.on_fill("A", Side.NO)
    assert status == "complete"
    assert c.open is False


def test_i5_inventory_hard_cap():
    cfg = ReserveConfig(max_abs_net=50.0, max_gross=200.0)
    inv = Inventory(yes=60, no=0)
    assert inventory_ok(inv, cfg) is False
    inv2 = Inventory(yes=30, no=30)
    assert inventory_ok(inv2, cfg) is True


def test_quote_ladder_symmetric():
    cfg = ReserveConfig(half_spread=0.01)
    q = quote_ladder(0.5, cfg)
    assert abs(q["bid_yes"] - 0.49) < 1e-12
    assert abs(q["ask_yes"] - 0.51) < 1e-12
