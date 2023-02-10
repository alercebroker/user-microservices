"""API for login and validating user data"""
from fastapi import FastAPI
from starlette_prometheus import metrics, PrometheusMiddleware

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
