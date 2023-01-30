from datetime import datetime

import pandas as pd
from astropy.time import Time
from fastapi import APIRouter, Body, Depends
from fastapi.responses import StreamingResponse
from query import BasePaginatedQuery

from . import filters, schemas
from .database import db, models


root = APIRouter()


def _datetime_to_iso(dataframe: pd.DataFrame, fields: str | list[str]):
    if isinstance(fields, str):  # pragma: no cover
        fields = [fields]
    for field in fields:
        dataframe[field] = dataframe[field].map(lambda x: x.isoformat(timespec="milliseconds"))


def _mjd_to_iso(dataframe: pd.DataFrame, fields: str | list[str]):
    if isinstance(fields, str):  # pragma: no cover
        fields = [fields]
    for field in fields:
        dataframe[field] = Time(dataframe[field], format="mjd").to_value("isot")


def _paginate(total: int, results: list, q: BasePaginatedQuery):
    return {
        "count": total,
        "next": q.page + 1 if q.skip + q.limit < total else None,
        "previous": q.page - 1 if q.page > 1 else None,
        "results": results,
    }


@root.get("/", response_model=schemas.PaginatedReportsByObject, tags=["queries"])
async def query_paginated_object_reports(q: filters.QueryByObject = Depends()):
    """Query reports grouped by object"""
    total = await db.count_documents(models.Report, q)
    results = await db.paginate_documents(models.Report, q)

    return _paginate(total, results, q)


@root.get("/reports", response_model=schemas.PaginatedReports, tags=["queries"])
async def query_paginated_reports(q: filters.QueryByReport = Depends()):
    """Query individual reports"""
    total = await db.count_documents(models.Report, q)
    results = await db.paginate_documents(models.Report, q)

    return _paginate(total, results, q)


@root.get("/count_by_day", response_model=list[schemas.ReportByDay], tags=["queries"])
async def count_reports_by_day(q: filters.QueryByDay = Depends()):
    """Query number of reports per day"""
    return await db.read_documents(models.Report, q)


@root.get("/count_by_user", response_model=list[schemas.ReportByUser], tags=["queries"])
async def count_reports_by_user(q: filters.QueryByUser = Depends()):
    """Query number of reports per day"""
    return await db.read_documents(models.Report, q)


@root.get("/csv_reports", response_class=StreamingResponse, responses={200: {"content": {"text/csv": {}}}}, tags=["download"])
async def download_report_table(q: filters.QueryByObject = Depends()):
    """Downloads a CSV with object and report information"""
    reports = await db.paginate_documents(models.Report, q)
    reports = pd.DataFrame(reports).drop(columns="users").set_index("object")
    _datetime_to_iso(reports, ["first_date", "last_date"])

    objects = db.query_objects(reports.index.unique().to_list())
    _mjd_to_iso(objects, ["first_detection", "last_detection"])
    reports = reports.join(objects)

    filename = f"{q.type if q.type else 'all'}_{datetime.now():%Y%m%d}.csv"
    headers = {"Content-Disposition": f"attachment; filename={filename}"}

    if q.order_by == "object":
        reports.sort_index(ascending=(q.direction == 1), inplace=True)
    else:
        reports.sort_values(by=q.order_by, ascending=(q.direction == 1), inplace=True)
    return StreamingResponse(iter(reports.to_csv()), media_type="text/csv", headers=headers)


@root.post("/", response_model=schemas.ReportOut, status_code=201, tags=["report"])
async def create_new_report(report: schemas.ReportIn = Body(...)):
    """Insert a new report in database. Date, ID and owner are set internally"""
    return await db.create_document(models.Report, report.dict())


@root.get("/{report_id}", response_model=schemas.ReportOut, tags=["report"])
async def get_report(report_id: str):
    """Retrieve single report based on its ID"""
    return await db.read_document(models.Report, report_id)


@root.patch("/{report_id}", response_model=schemas.ReportOut, tags=["report"])
async def update_existing_report(report_id: str, report: schemas.ReportUpdate = Body(...)):
    """Updates one or more fields of an existing report based on its ID"""
    return await db.update_document(models.Report, report_id, report.dict(exclude_none=True))


@root.put("/{report_id}", response_model=schemas.ReportOut, tags=["report"])
async def replace_existing_report(report_id: str, report: schemas.ReportIn = Body(...)):
    """Updates the full report based on its ID"""
    return await db.update_document(models.Report, report_id, report.dict())


@root.delete("/{report_id}", status_code=204, tags=["report"])
async def delete_report(report_id: str):
    """Deletes existing report based on its ID"""
    await db.delete_document(models.Report, report_id)
