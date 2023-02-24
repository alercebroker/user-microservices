"""API for login and validating user data"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette_prometheus import metrics, PrometheusMiddleware
from db_handler import DocumentNotFound
from jwt.exceptions import MissingRequiredClaimError, ExpiredSignatureError
from users.users.routes.password_auth import router as password_auth_route
from users.users.routes.token import router as token_route

app = FastAPI(
    title="Users  API",
    description=__doc__,
    contact={
        "name": "ALeRCE Broker",
        "email": "alercebroker@gmail.com",
        "url": "https://alerce.science"
    }
)

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)
app.include_router(password_auth_route)
app.include_router(token_route)

@app.exception_handler(DocumentNotFound)
async def document_not_found(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(MissingRequiredClaimError)
async def document_not_found(request, exc):
    return JSONResponse(status_code=403, content={"detail": str(exc)})

@app.exception_handler(ExpiredSignatureError)
async def document_not_found(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})