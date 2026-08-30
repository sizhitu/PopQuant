# PopQuant

Hypothesis-driven quant research OS. Phase 0 focuses on **executable math** for prediction markets:

1. Depth-integrated executable quotes (not top-of-book fantasy)
2. Inventory reservation price + single-leg circuit breaker
3. Fee-aware EV + calibration logs

No exchange keys. No live order placement in this phase.

## Install

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Test

```bash
pytest -q
```

## Layout

```
popquant/exec_math/
  types.py         # Side, Level, Book, Inventory, Intent, FillLog
  executable.py    # executable_cost, complementary_edge
  inventory.py     # reservation_price, LegCircuit, inventory_ok
  ev_calib.py      # net_ev, size_fractional_kelly, CalibrationBook
tests/
  test_executable.py
  test_inventory.py
  test_ev_calib.py
```

## Hard gates (no size-up if violated)

- Insufficient depth or `edge < δ`
- Single-leg circuit open
- `net_ev ≤ 0`
- Inventory over caps
- Incomplete fill logs

## License

MIT
