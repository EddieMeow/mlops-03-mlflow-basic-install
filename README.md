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

`mlflow ui` alone uses the local filesystem (`mlruns/`) as its store. To use a
**SQLite backend store** instead — which is what you need for the model registry and
for faster, queryable run metadata — run `mlflow server` with a `--backend-store-uri`:

```bash
uv run mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlartifacts \
  --host 127.0.0.1 \
  --port 5464
```

Then open http://127.0.0.1:5464

Any free port works — `5464` is just the one used here. Pass a different `--port` if
it's taken. To pick a free one automatically:

```bash
PORT=$(python3 -c "import socket; s=socket.socket(); s.bind(('127.0.0.1',0)); print(s.getsockname()[1]); s.close()")
uv run mlflow server --backend-store-uri sqlite:///mlflow.db --port $PORT
```

### What the flags do

| Flag | Purpose |
| --- | --- |
| `--backend-store-uri sqlite:///mlflow.db` | Store run metadata (params, metrics, tags) in a SQLite file instead of flat files. Required for the model registry. |
| `--default-artifact-root ./mlartifacts` | Where artifacts (files, models) are written |
| `--host 127.0.0.1` | Bind to localhost only — not reachable from other machines |
| `--port 5464` | Port to serve the UI and REST API on |

Note the three slashes in `sqlite:///mlflow.db` — two for the URI scheme plus one
starting the relative path. The file is created on first run.

### Point your code at the server

With a backend store you log over HTTP rather than writing to `mlruns/` directly:

```bash
export MLFLOW_TRACKING_URI=http://127.0.0.1:5464
uv run python main.py
```

Or set it in code with `mlflow.set_tracking_uri("http://127.0.0.1:5464")`.

### Verify the server

```bash
curl http://127.0.0.1:5464/health          # -> OK
curl -X POST http://127.0.0.1:5464/api/2.0/mlflow/experiments/search \
  -H "Content-Type: application/json" -d '{"max_results":10}'
```

Inspect the SQLite store directly:

```bash
sqlite3 mlflow.db "select experiment_id, name from experiments;"
sqlite3 mlflow.db "select run_uuid, status from runs;"
```

## Log a sample run

```bash
uv run python main.py
```

This creates an experiment called `basic-install-check` and logs one run. Where the
data lands depends on `MLFLOW_TRACKING_URI`: unset, it goes to `mlruns/`; set to the
server, it goes into `mlflow.db`. Both are git-ignored.

## Kubernetes cluster (kind)

A local single-node Kubernetes cluster for deploying MLflow to k8s.
[kind](https://kind.sigs.k8s.io/) runs Kubernetes inside Docker containers, so
**Docker must be running** first.

### Prerequisites

```bash
brew install kind        # kind itself
brew install kubectl     # if you don't already have it
```

Versions used here: kind 0.33.0, kubectl v1.34.1, Kubernetes v1.37.0.

### Create the cluster

```bash
kind create cluster --name basic-mlflow-cluster
```

First run downloads the node image (~1 GB) and takes a few minutes. This also sets
your kubectl context to `kind-basic-mlflow-cluster` automatically.

### Verify it

```bash
kind get clusters                    # -> basic-mlflow-cluster
kubectl config current-context       # -> kind-basic-mlflow-cluster
kubectl get nodes                    # -> control-plane, Ready
kubectl get pods -n kube-system      # all Running
```

The node reports `NotReady` for the first ~20 seconds while the CNI starts. Wait for
it rather than assuming a failure:

```bash
kubectl wait --for=condition=Ready node --all --timeout=180s
```

### Cluster management

| Command | Purpose |
| --- | --- |
| `kind get clusters` | List local kind clusters |
| `kubectl config use-context kind-basic-mlflow-cluster` | Switch kubectl to this cluster |
| `kind load docker-image <image> --name basic-mlflow-cluster` | Make a local image available to the cluster (kind can't pull from your host daemon) |
| `kind delete cluster --name basic-mlflow-cluster` | Delete the cluster and everything in it |

Note that a kind cluster's state lives in Docker — stopping Docker Desktop stops the
cluster, and deleting the container destroys it. It's disposable by design; recreate
with the same command.

## Helm

[Helm](https://helm.sh/) is the package manager for Kubernetes — it installs
*charts* (templated bundles of Kubernetes YAML) instead of you hand-writing a
Deployment, Service, ConfigMap and PVC for every app.

### Install

```bash
brew install helm
helm version
```

Version used here: **Helm v4.3.0**. Helm reads the same kubeconfig as kubectl, so it
targets whatever your current context is — check with `kubectl config current-context`
before installing anything.

### Concepts

| Term | Meaning |
| --- | --- |
| **Chart** | The package: templated k8s manifests plus metadata |
| **Values** | Configuration knobs (`values.yaml`); override with `--set` or `-f` |
| **Release** | One installed instance of a chart in the cluster |
| **Repository** | Where charts are hosted |

### Add a chart repository

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm search repo bitnami/postgresql
```

### Common Helm commands

| Command | Purpose |
| --- | --- |
| `helm install <release> <chart>` | Install a chart as a named release |
| `helm install <release> <chart> --wait` | Install and block until pods are Ready |
| `helm list` | List releases in the current namespace |
| `helm upgrade <release> <chart> --set key=value` | Change config / upgrade a release |
| `helm rollback <release> <revision>` | Roll back to an earlier revision |
| `helm uninstall <release>` | Remove the release and its resources |
| `helm show values <chart>` | Print a chart's configurable values |
| `helm template <release> <chart>` | Render manifests locally without installing |

`helm upgrade` and `helm rollback` are the real advantage over raw `kubectl apply`:
Helm keeps a revision history per release, so a bad deploy is one command to undo.

### Relevance to MLflow

Deploying MLflow to Kubernetes usually means three Helm releases: MLflow itself,
**PostgreSQL** to replace the SQLite backend store, and **MinIO** (S3-compatible) to
replace the local `mlartifacts/` directory — since pods are ephemeral and a SQLite
file on local disk doesn't survive a restart or scale past one replica.

## Project command reference

| Command | Purpose |
| --- | --- |
| `uv sync` | Install/refresh the environment from `uv.lock` |
| `uv add <pkg>` | Add a dependency and update the lock |
| `uv remove <pkg>` | Remove a dependency |
| `uv run <cmd>` | Run a command in the venv without activating it |
| `source .venv/bin/activate` | Activate the venv for plain `python3` / `pip` use |
| `uv run mlflow server --backend-store-uri sqlite:///mlflow.db --port <n>` | Start the tracking server with a SQLite backend |

Adding packages with `pip` will **not** update `pyproject.toml` or `uv.lock`. To keep
the pinned setup reproducible for others, prefer `uv add <pkg>`.
