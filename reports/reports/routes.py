from fastapi import APIRouter, Body, Depends

from . import database, filters, schemas


root = APIRouter()


@root.get("/", response_model=schemas.PaginatedReports)
async def get_report_list(q: filters.QueryByReport = Depends()):
    """Query reports"""
    return await database.get_connection().read_paginated_documents(database.Report, q)


@root.get("/by_object", response_model=schemas.PaginatedReportsByObject)
async def get_report_list_by_object(q: filters.QueryByObject = Depends()):
    """Query reports grouped by object"""
    return await database.get_connection().read_paginated_documents(database.Report, q)


@root.get("/count_by_day", response_model=list[schemas.ReportByDay])
async def count_reports_by_day(q: filters.QueryByDay = Depends()):
    """Query number of reports per day"""
    return await database.get_connection().read_multiple_documents(database.Report, q)


@root.post("/", response_model=schemas.ReportOut, status_code=201)
async def create_new_report(report: schemas.ReportIn = Body(...)):
    """Insert a new report in database. Date, ID and owner are set internally"""
    return await database.get_connection().create_document(database.Report, report)


@root.get("/{report_id}", response_model=schemas.ReportOut)
async def get_single_report(report_id: str):
    """Retrieve single report based on its ID"""
    return await database.get_connection().read_document(database.Report, report_id)


@root.patch("/{report_id}", response_model=schemas.ReportOut)
async def update_existing_report(report_id: str, report: schemas.ReportUpdate = Body(...)):
    """Updates one or more fields of an existing report based on its ID"""
    return await database.get_connection().update_document(database.Report, report_id, report)


@root.put("/{report_id}", response_model=schemas.ReportOut)
async def replace_existing_report(report_id: str, report: schemas.ReportIn = Body(...)):
    """Updates the full report based on its ID"""
    return await database.get_connection().update_document(database.Report, report_id, report)


@root.delete("/{report_id}", status_code=204)
async def delete_report(report_id: str):
    """Deletes existing report based on its ID"""
    await database.get_connection().delete_document(database.Report, report_id)
