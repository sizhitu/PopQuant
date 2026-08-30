import time

from popquant.exec_math.types import Book, FeeModel, Level
from popquant.exec_math.executable import complementary_edge, executable_cost


def test_e1_single_level():
    levels = (Level(0.40, 100),)
    cost = executable_cost(levels, 50)
    assert cost == 20.0
    assert abs(cost / 50 - 0.40) < 1e-12


def test_e2_multi_level_vwap():
    levels = (Level(0.30, 20), Level(0.40, 80))
    cost = executable_cost(levels, 50)
    assert cost == 18.0  # 0.30*20 + 0.40*30
    assert abs(cost / 50 - 0.36) < 1e-12


def test_e3_insufficient_depth():
    levels = (Level(0.40, 30),)
    assert executable_cost(levels, 50) is None


def test_e4_complementary_edge_positive():
    book = Book(
        yes_asks=(Level(0.45, 100),),
        no_asks=(Level(0.50, 100),),
        yes_bids=(),
        no_bids=(),
        ts=time.time(),
    )
    fee = FeeModel(taker_bps=0.0, maker_bps=0.0)
    res = complementary_edge(book, qty=10, fee=fee, delta=0.02)
    assert res is not None
    assert abs(res["edge"] - 0.05) < 1e-9
    assert abs(res["vwap_yes"] - 0.45) < 1e-12
    assert abs(res["vwap_no"] - 0.50) < 1e-12


def test_e5_depth_kills_paper_arb():
    # Paper best looks fine; depth pushes cost over 1 - delta
    book = Book(
        yes_asks=(Level(0.48, 5), Level(0.55, 100)),
        no_asks=(Level(0.48, 5), Level(0.55, 100)),
        yes_bids=(),
        no_bids=(),
        ts=time.time(),
    )
    fee = FeeModel(taker_bps=0.0, maker_bps=0.0)
    # qty large enough to walk into bad levels
    res = complementary_edge(book, qty=50, fee=fee, delta=0.02)
    assert res is None
