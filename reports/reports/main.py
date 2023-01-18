"""API for interacting with reports"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError
from starlette_prometheus import metrics, PrometheusMiddleware

from .database import get_connection, DocumentNotFound
from .routes import root


app = FastAPI(
    title="Reports API",
    description=__doc__,
    contact={
        "name": "ALeRCE Broker",
        "email": "alercebroker@gmail.com",
        "url": "https://alerce.science"
    }
)

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

app.include_router(root)


@app.on_event("startup")
async def startup():
    await get_connection().connect()
    await get_connection().create_db()


@app.on_event("shutdown")
async def shutdown():
    await get_connection().close()


@app.exception_handler(DuplicateKeyError)
async def bad_request_for_duplicates(request, exc):
    message = f"Duplicate document in database: {str(exc)}"
    return JSONResponse(status_code=400, content={"detail": message})


@app.exception_handler(DocumentNotFound)
async def document_not_found(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})
