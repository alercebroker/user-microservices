from fastapi import APIRouter, Body, Depends

from . import database, filters, models


root = APIRouter()


@root.get("/", response_model=models.PaginatedReports)
async def get_report_list(q: filters.QueryByReport = Depends()):
    """Query reports"""
    return await database.read_paginated_reports(q)


@root.get("/by_object", response_model=models.PaginatedReportsByObject)
async def get_report_list_by_object(q: filters.QueryByObject = Depends()):
    """Query reports grouped by object"""
    return await database.read_paginated_reports(q)


@root.get("/count_by_day", response_model=list[models.ReportByDay])
async def count_reports_by_day(q: filters.QueryByDay = Depends()):
    """Query number of reports per day"""
    return await database.read_all_reports(q)


@root.post("/", response_model=models.ReportOut, status_code=201)
async def create_new_report(report: models.ReportIn = Body(...)):
    """Insert a new report in database. Date, ID and owner are set internally"""
    return await database.create_report(report)


@root.get("/{report_id}", response_model=models.ReportOut)
async def get_single_report(report_id: str):
    """Retrieve single report based on its ID"""
    return await database.read_report(report_id)


@root.patch("/{report_id}", response_model=models.ReportOut)
async def update_existing_report(report_id: str, report: models.ReportUpdate = Body(...)):
    """Updates one or more fields of an existing report based on its ID"""
    return await database.update_report(report_id, report)


@root.put("/{report_id}", response_model=models.ReportOut)
async def replace_existing_report(report_id: str, report: models.ReportIn = Body(...)):
    """Updates the full report based on its ID"""
    return await database.update_report(report_id, report)


@root.delete("/{report_id}", status_code=204)
async def delete_report(report_id: str):
    """Deletes existing report based on its ID"""
    await database.delete_report(report_id)
