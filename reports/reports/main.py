"""API for interacting with reports"""
from db_handler import DocumentNotFound
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError
from starlette_prometheus import metrics, PrometheusMiddleware

from .database import db
from .routes import root
from . import __version__


app = FastAPI(
    title="Reports API",
    description=__doc__,
    version=__version__,
    contact={"name": "ALeRCE Broker", "email": "alercebroker@gmail.com", "url": "https://alerce.science"},
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

app.include_router(root)


@app.on_event("startup")
async def startup():
    await db.connect()
    await db.create_db()


@app.on_event("shutdown")
async def shutdown():
    await db.close()


@app.exception_handler(DuplicateKeyError)
async def bad_request_for_duplicates(request, exc):
    message = f"Duplicate document in collection: {str(exc)}"
    return JSONResponse(status_code=400, content={"detail": message})


@app.exception_handler(ServerSelectionTimeoutError)
async def database_is_down(request, exc):
    message = f"Cannot connect to MongoDB server: {str(exc)}"
    return JSONResponse(status_code=503, content={"detail": message})


@app.exception_handler(ConnectionError)
async def connection_error(request, exc):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(DocumentNotFound)
async def document_not_found(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})
