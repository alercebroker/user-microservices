"""API for interacting with reports"""
from fastapi import FastAPI, Body, Depends
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError

from . import database
from .filters import QueryByReport, QueryByObject, QueryByDay
from .models import Report, ReportInsert, ReportUpdate, ReportByDay, PaginatedReports, PaginatedReportsByObject


app = FastAPI()
connection = database.connection


@app.on_event("startup")
async def startup():
    await connection.connect()
    await connection.create_db()


@app.on_event("shutdown")
async def shutdown():
    await connection.close()


@app.exception_handler(DuplicateKeyError)
async def bad_request_for_duplicates(request, exc):
    message = f"Duplicate document in database: {str(exc)}"
    return JSONResponse(status_code=400, content={"detail": message})


@app.exception_handler(database.DocumentNotFound)
async def document_not_found(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.get("/", response_model=PaginatedReports)
async def get_report_list(q: QueryByReport = Depends()):
    """Query all reports"""
    return database.read_paginated_reports(connection, q)


@app.get("/by_object", response_model=PaginatedReportsByObject)
async def get_report_list_by_object(q: QueryByObject = Depends()):
    """Query reports by reported object"""
    return await database.read_paginated_reports(connection, q)


@app.get("/count_by_day", response_model=list[ReportByDay])
async def count_reports_by_day(q: QueryByDay = Depends()):
    """Query number of reports by day"""
    return await database.read_all_reports(connection, q)


@app.post("/", response_model=Report, status_code=201)
async def create_new_report(report: ReportInsert = Body(...)):
    """Insert a new report in database. Date, ID and owner are set automatically"""
    return await database.create_report(connection, report)


@app.get("/{report_id}", response_model=Report)
async def get_single_report(report_id: str):
    """Retrieve single report based on its ID"""
    return await database.read_report(connection, report_id)


@app.patch("/{report_id}", response_model=Report)
async def update_existing_report(report_id: str, report: ReportUpdate = Body(...)):
    """Updates an existing report based on its ID"""
    return await database.update_report(connection, report_id, report)


@app.put("/{report_id}", response_model=Report)
async def replace_existing_report(report_id: str, report: ReportInsert = Body(...)):
    """Replaces an existing report based on its ID"""
    return await database.update_report(connection, report_id, report)


@app.delete("/{report_id}", status_code=204)
async def delete_report(report_id: str):
    """Deletes existing report based on its ID"""
    await database.delete_report(connection, report_id)
