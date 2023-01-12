"""API for interacting with reports"""
from fastapi import FastAPI, Body, Depends, HTTPException

from . import crud
from .database import connection
from .filters import QueryByReport, QueryByObject, QueryByDay
from .models import Report, InsertReport, PaginatedReports, PaginatedReportsByObject, PaginatedReportsByDay


app = FastAPI()


@app.on_event("startup")
async def startup():
    await connection.connect()


@app.on_event("shutdown")
async def shutdown():
    await connection.close()


@app.get("/", response_model=PaginatedReports, response_description="Report list")
async def get_report_list(q: QueryByReport = Depends()):
    """Query all reports"""
    return await crud.read_paginated_reports(connection, q)


@app.get("/by_object", response_model=PaginatedReportsByObject, response_description="Report list grouped by object")
async def get_report_list_by_object(q: QueryByObject = Depends()):
    """Query reports by reported object"""
    return await crud.read_paginated_reports(connection, q)


@app.get("/count_by_day", response_model=PaginatedReportsByDay, response_description="Count of reports by day")
async def count_reports_by_day(q: QueryByDay = Depends()):
    """Query number of reports by day"""
    return await crud.read_paginated_reports(connection, q)


@app.post("/", response_model=Report, response_description="Created report", status_code=201)
async def create_new_report(report: InsertReport = Body(...)):
    """Insert a new report in database. Date, ID and owner are set automatically"""
    return await crud.create_report(connection, report)


@app.get("/{report_id}", response_model=Report, response_description="Requested report")
async def get_single_report(report_id: str):
    """Retrieve single report based on its ID"""
    report = await crud.read_report(connection, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report ID {report_id} not found")
    return report


@app.put("/{report_id}", response_model=Report, response_description="Report updated")
async def update_existing_report(report_id: str, report: InsertReport = Body(...)):
    """Updates an existing report based on its ID"""
    report = await crud.update_report(connection, report_id, report)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report ID {report_id} not found")
    return report


@app.delete("/{report_id}", response_description="Report deleted", status_code=204)
async def delete_report(report_id: str):
    """Deletes existing report based on its ID"""
    deleted = await crud.delete_report(connection, report_id)
    if deleted:
        return
    raise HTTPException(status_code=404, detail=f"Report ID {report_id} not found")
