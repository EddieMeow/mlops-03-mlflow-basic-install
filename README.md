# mlops-03-mlflow-basic-install

Basic MLflow installation and setup — part of an MLOps practice series.

Uses [uv](https://docs.astral.sh/uv/) for environment and dependency management.

## Setup

Install uv (once, if you don't have it):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Sync the environment — this creates `.venv` and installs the locked dependencies:

```bash
uv sync
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

## Common commands

| Command | Purpose |
| --- | --- |
| `uv sync` | Install/refresh the environment from `uv.lock` |
| `uv add <pkg>` | Add a dependency and update the lock |
| `uv remove <pkg>` | Remove a dependency |
| `uv run <cmd>` | Run a command inside the project environment |

Python version is pinned in `.python-version`; exact dependency versions are pinned in `uv.lock`.
