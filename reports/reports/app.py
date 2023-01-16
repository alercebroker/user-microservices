"""API for interacting with reports"""
from fastapi import FastAPI, Body, Depends
from fastapi.responses import JSONResponse
from pymongo import errors

from . import database
from .filters import QueryByReport, QueryByObject, QueryByDay
from .models import ReportOut, ReportIn, ReportUpdate, ReportByDay, PaginatedReports, PaginatedReportsByObject


app = FastAPI(
    title="Reports API",
    description=__doc__,
    contact={
        "name": "ALeRCE Broker",
        "email": "alercebroker@gmail.com",
        "url": "https://alerce.science"
    }
)


@app.on_event("startup")
async def startup():
    await database.connection.connect()
    await database.connection.create_db()


@app.on_event("shutdown")
async def shutdown():
    await database.connection.close()


@app.exception_handler(errors.DuplicateKeyError)
async def bad_request_for_duplicates(request, exc):
    message = f"Duplicate document in database: {str(exc)}"
    return JSONResponse(status_code=400, content={"detail": message})


@app.exception_handler(errors.ServerSelectionTimeoutError)
async def bad_request_for_duplicates(request, exc):
    message = f"Cannot connect to database server: {str(exc)}"
    return JSONResponse(status_code=503, content={"detail": message})


@app.exception_handler(database.DocumentNotFound)
async def document_not_found(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.get("/", response_model=PaginatedReports)
async def get_report_list(q: QueryByReport = Depends()):
    """Query reports"""
    return await database.read_paginated_reports(q)


@app.get("/by_object", response_model=PaginatedReportsByObject)
async def get_report_list_by_object(q: QueryByObject = Depends()):
    """Query reports grouped by object"""
    return await database.read_paginated_reports(q)


@app.get("/count_by_day", response_model=list[ReportByDay])
async def count_reports_by_day(q: QueryByDay = Depends()):
    """Query number of reports per day"""
    return await database.read_all_reports(q)


@app.post("/", response_model=ReportOut, status_code=201)
async def create_new_report(report: ReportIn = Body(...)):
    """Insert a new report in database. Date, ID and owner are set internally"""
    return await database.create_report(report)


@app.get("/{report_id}", response_model=ReportOut)
async def get_single_report(report_id: str):
    """Retrieve single report based on its ID"""
    return await database.read_report(report_id)


@app.patch("/{report_id}", response_model=ReportOut)
async def update_existing_report(report_id: str, report: ReportUpdate = Body(...)):
    """Updates one or more fields of an existing report based on its ID"""
    return await database.update_report(report_id, report)


@app.put("/{report_id}", response_model=ReportOut)
async def replace_existing_report(report_id: str, report: ReportIn = Body(...)):
    """Updates the full report based on its ID"""
    return await database.update_report(report_id, report)


@app.delete("/{report_id}", status_code=204)
async def delete_report(report_id: str):
    """Deletes existing report based on its ID"""
    await database.delete_report(report_id)
