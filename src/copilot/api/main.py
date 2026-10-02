from fastapi import FastAPI

app = FastAPI(title="Domain Copilot", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    # Placeholder: will check database connectivity once the DB is wired in.
    return {"status": "ready"}