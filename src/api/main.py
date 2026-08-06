import logging
from importlib.metadata import PackageNotFoundError, version

from fastapi import FastAPI

from src.api.config import settings
from src.api.routes import router

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

try:
    APP_VERSION = version("sdr-lead-classification")
except PackageNotFoundError:
    APP_VERSION = "0.0.0"

app = FastAPI(
    title="SDR Lead Classification API",
    description="API para classificação e diagnóstico de leads B2B via WhatsApp",
    version=APP_VERSION,
)

app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/version")
def app_version():
    return {"version": APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
