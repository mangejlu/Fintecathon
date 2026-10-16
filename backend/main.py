"""API routes for Landed."""

from fastapi import FastAPI

app = FastAPI(title="Landed")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
