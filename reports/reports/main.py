"""API for interacting with reports"""
from db_handler import DocumentNotFound
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError
from starlette_prometheus import metrics, PrometheusMiddleware

from . import __version__, database, routes, settings


settings = settings.get_settings()

app = FastAPI(
    title="Reports API",
    description=__doc__,
    version=__version__,
    root_path=settings.root_path,
    contact={"name": "ALeRCE Broker", "email": "alercebroker@gmail.com", "url": "https://alerce.science"},
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

app.include_router(routes.root)


@app.on_event("startup")
async def startup():
    await database.get_connection().connect()
    await database.get_connection().create_db()


@app.on_event("shutdown")
async def shutdown():
    await database.get_connection().close()


@app.exception_handler(DuplicateKeyError)
async def bad_request_for_duplicates(request, exc):
    return JSONResponse(status_code=400, content={"detail": "Duplicate document keys in collection"})


@app.exception_handler(ServerSelectionTimeoutError)
async def database_is_down(request, exc):
    return JSONResponse(status_code=503, content={"detail": "Cannot connect to MongoDB server"})


@app.exception_handler(ConnectionError)
async def connection_error(request, exc):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(DocumentNotFound)
async def document_not_found(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})
