# mlops-03-mlflow-basic-install

Basic MLflow installation and setup — part of an MLOps practice series.

This repo is a minimal, reproducible MLflow environment: it pins Python and every
dependency version so the same setup can be recreated on any machine, and includes a
smoke-test script that proves the install works by logging a real MLflow run.

**What's here:**

| File | What it's for |
| --- | --- |
| `pyproject.toml` | Declares the project and its dependencies (`mlflow`) |
| `uv.lock` | Exact pinned versions of all ~60 transitive packages |
| `.python-version` | Pins the Python interpreter (3.12) |
| `main.py` | Smoke test — logs a param, metric, and artifact to one MLflow run |

Current versions: **MLflow 3.16.0** on **Python 3.12.8**.

## Setup

The environment lives in `.venv/` in this folder. Everything below installs into
that one venv — nothing is installed into your system Python.

### Option A — uv (recommended)

[uv](https://docs.astral.sh/uv/) reads `uv.lock` and reproduces the exact pinned
versions, so you get an identical environment every time.

Install uv (once, if you don't have it):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create `.venv` and install all locked dependencies:

```bash
uv sync
```

### Option B — python3 and pip

If you'd rather use the standard tooling, activate the venv and install with pip.
Note that pip resolves versions fresh rather than reading `uv.lock`, so you may get
newer versions than the ones pinned here.

```bash
source .venv/bin/activate
python3 -m pip install mlflow
```

Once activated, `python3` points at `.venv/bin/python3` rather than your system
Python — confirm with `which python3`. Use `deactivate` to exit.

If the venv doesn't exist yet, create it first with `python3 -m venv .venv`.
(A venv created by `uv sync` has no `pip` inside it by default; add one with
`uv pip install pip` — this repo's venv already has it.)

## Verify the install

```bash
source .venv/bin/activate
python3 -c "import mlflow; print(mlflow.__version__)"
mlflow --version
```

Or without activating, via uv:

```bash
uv run mlflow --version
```

## Run the tracking server

```bash
uv run mlflow ui
```

Then open http://127.0.0.1:5000

## Log a sample run

```bash
uv run python main.py
```

This creates an experiment called `basic-install-check` and logs one run. Local run
data is written to `mlruns/` (git-ignored) — open the UI above to view it.

## Common commands

| Command | Purpose |
| --- | --- |
| `uv sync` | Install/refresh the environment from `uv.lock` |
| `uv add <pkg>` | Add a dependency and update the lock |
| `uv remove <pkg>` | Remove a dependency |
| `uv run <cmd>` | Run a command in the venv without activating it |
| `source .venv/bin/activate` | Activate the venv for plain `python3` / `pip` use |

Adding packages with `pip` will **not** update `pyproject.toml` or `uv.lock`. To keep
the pinned setup reproducible for others, prefer `uv add <pkg>`.
