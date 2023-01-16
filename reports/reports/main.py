"""API for interacting with reports"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pymongo import errors

from .database import connection, DocumentNotFound
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

app.include_router(root)


@app.on_event("startup")
async def startup():
    await connection.connect()
    await connection.create_db()


@app.on_event("shutdown")
async def shutdown():
    await connection.close()


@app.exception_handler(errors.DuplicateKeyError)
async def bad_request_for_duplicates(request, exc):
    message = f"Duplicate document in database: {str(exc)}"
    return JSONResponse(status_code=400, content={"detail": message})


@app.exception_handler(errors.ServerSelectionTimeoutError)
async def bad_request_for_duplicates(request, exc):
    message = f"Cannot connect to database server: {str(exc)}"
    return JSONResponse(status_code=503, content={"detail": message})


@app.exception_handler(DocumentNotFound)
async def document_not_found(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})
