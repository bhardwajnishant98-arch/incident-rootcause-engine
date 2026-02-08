from fastapi import FastAPI

app = FastAPI(title="Incident Root Cause Analysis Engine")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
