"""API for interacting with reports"""
from fastapi import FastAPI, Body, Depends, HTTPException
from pymongo.errors import DuplicateKeyError

from . import crud
from .database import connection
from .filters import QueryByReport, QueryByObject, QueryByDay
from .models import Report, InsertReport, ReportByDay, PaginatedReports, PaginatedReportsByObject


app = FastAPI()


@app.on_event("startup")
async def startup():
    await connection.connect()
    await connection.create_db()


@app.on_event("shutdown")
async def shutdown():
    await connection.close()


@app.get("/", response_model=PaginatedReports)
async def get_report_list(q: QueryByReport = Depends()):
    """Query all reports"""
    return await crud.read_paginated_reports(connection, q)


@app.get("/by_object", response_model=PaginatedReportsByObject)
async def get_report_list_by_object(q: QueryByObject = Depends()):
    """Query reports by reported object"""
    return await crud.read_paginated_reports(connection, q)


@app.get("/count_by_day", response_model=list[ReportByDay])
async def count_reports_by_day(q: QueryByDay = Depends()):
    """Query number of reports by day"""
    return await crud.read_all_reports(connection, q)


@app.post("/", response_model=Report, status_code=201)
async def create_new_report(report: InsertReport = Body(...)):
    """Insert a new report in database. Date, ID and owner are set automatically"""
    try:
        return await crud.create_report(connection, report)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Duplicate object and report type for owner")


@app.get("/{report_id}", response_model=Report)
async def get_single_report(report_id: str):
    """Retrieve single report based on its ID"""
    report = await crud.read_report(connection, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report ID {report_id} not found")
    return report


@app.put("/{report_id}", response_model=Report)
async def update_existing_report(report_id: str, report: InsertReport = Body(...)):
    """Updates an existing report based on its ID"""
    try:
        report = await crud.update_report(connection, report_id, report)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Duplicate object and report type for owner")
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report ID {report_id} not found")
    return report


@app.delete("/{report_id}", status_code=204)
async def delete_report(report_id: str):
    """Deletes existing report based on its ID"""
    deleted = await crud.delete_report(connection, report_id)
    if deleted:
        return
    raise HTTPException(status_code=404, detail=f"Report ID {report_id} not found")
