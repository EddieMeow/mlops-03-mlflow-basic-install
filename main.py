"""Minimal MLflow smoke test: logs one run with a param, a metric, and an artifact."""

import mlflow


def main() -> None:
    mlflow.set_experiment("basic-install-check")

    with mlflow.start_run() as run:
        mlflow.log_param("alpha", 0.5)
        mlflow.log_metric("rmse", 0.83)
        mlflow.log_text("hello from mlflow", "notes.txt")
        print(f"Logged run {run.info.run_id}")

    print("Done. View it with: uv run mlflow ui")


if __name__ == "__main__":
    main()
