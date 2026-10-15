# Contributing

## Run the checks

Every push runs these on GitHub (see `.github/workflows/checks.yml`). Run them locally first:

```powershell
.\.venv\Scripts\ruff.exe check .          # lint (add --fix for automatic fixes)
.\.venv\Scripts\ruff.exe format .         # format
.\.venv\Scripts\mypy.exe                  # strict type checking
.\.venv\Scripts\python.exe -m pytest      # science tests + code-rule tests
```

All four must pass with zero warnings.

## Code standards: NASA/JPL "Power of 10", adapted to Python

The [Power of 10 rules](https://en.wikipedia.org/wiki/The_Power_of_10:_Rules_for_Developing_Safety-Critical_Code)
were written for safety-critical C. Here's how each one is applied in this project.

| # | Rule | How it's applied here |
|---|---|---|
| 1 | Simple control flow, no recursion | Ruff complexity limits (`C90`, `PLR0912`); `tests/test_code_rules.py` rejects recursion |
| 2 | Every loop has a fixed upper bound | `tests/test_code_rules.py` rejects `while True`; prefer `for` over a known range |
| 3 | No dynamic memory allocation after initialization | Doesn't map to Python. Guideline: preallocate NumPy arrays instead of growing them in hot loops |
| 4 | Functions fit on one page (≤ 60 lines) | `tests/test_code_rules.py`; Ruff `PLR0915` caps statements at 50 |
| 5 | Check assumptions | Validate inputs with explicit `raise ValueError(...)`, not `assert`, which `python -O` strips out |
| 6 | Declare data at the smallest possible scope | Ruff `PLW0603` bans `global`; prefer function arguments and frozen dataclasses |
| 7 | Check return values and parameters | mypy `--strict`; check results like `solve_ivp(...).success` |
| 8 | Limit the preprocessor | No `eval`/`exec` (Ruff `S307`, `S102`), no star imports (`F403`), no metaprogramming |
| 9 | Limit pointer use | Doesn't map to Python. Guideline: avoid deep attribute chains and mutable shared state |
| 10 | Compile with all warnings on, zero warnings | Ruff + mypy strict + pytest `filterwarnings = error`, enforced in CI |

## Ground rules for data

Open-source tools and public datasets only, with the source and license noted. No personal or
health data (PII/PHI) about anyone. See the README.