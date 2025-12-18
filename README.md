# damo2

[![CI](https://github.com/Damien157/damo2/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Damien157/damo2/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/Damien157/damo2/branch/main/graph/badge.svg)](https://codecov.io/gh/Damien157/damo2)

Overview
--------

This repository contains a small Python module `apply_anchor.py` implementing an `apply_anchor` function and a comprehensive pytest suite. The purpose is to validate anchor invariants and issue corrective actions when necessary.

Files of interest
- `apply_anchor.py` — implementation and a small runnable example.
- `tests/` — pytest test suite covering invariants, edge cases, and helpers.
- `.github/workflows/ci.yml` — CI workflow running tests and uploading coverage to Codecov.
- `requirements.txt` — minimal test/runtime dependencies.

Quickstart
----------

1. Clone the repo (or the PR branch):

```bash
git clone https://github.com/Damien157/damo2.git
cd damo2
# or clone the feature branch
git clone --branch tests/add-coverage https://github.com/Damien157/damo2.git
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

3. Run the example module:

```bash
python apply_anchor.py
```

4. Run tests locally:

```bash
pytest -q
# to see coverage report
pytest --cov=. --cov-report=term-missing
```

Codecov & CI
-------------

- GitHub Actions runs the test matrix and uploads coverage to Codecov. For private repos you must add the Codecov repository token as a secret `CODECOV_TOKEN` in the repository Settings → Secrets → Actions.
- Coverage configuration is in `.codecov.yml` and `.coveragerc`.

Contributing
------------

1. Create a branch for your changes.
2. Add tests for new behaviors.
3. Open a pull request and request review.

License
-------

No license specified. Add a `LICENSE` file if you intend to open-source this repository.

Contact
-------

Open an issue or PR on GitHub: https://github.com/Damien157/damo2
