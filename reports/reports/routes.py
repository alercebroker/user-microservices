import pandas as pd
from db_handler import DocumentNotFound
from fastapi import APIRouter, Body, Depends
from fastapi.responses import StreamingResponse

from . import database, filters, schemas
from .database import db, models


root = APIRouter()


def _check_exists(document: dict | None, oid: str):
    if document is None:
        raise DocumentNotFound(oid)
    return document


def _datetime_to_iso(dataframe: pd.DataFrame, fields: str | list[str]):
    if isinstance(fields, str):
        fields = [fields]
    for field in fields:
        dataframe[field].map(lambda x: x.isoformat(timespec="milliseconds"))


@root.get("/", response_model=schemas.PaginatedReports)
async def get_report_list(q: filters.QueryByReport = Depends()):
    """Query reports"""
    total = await db.count_documents(models.Report, q)
    results = db.paginate_documents(models.Report, q)

    return {
        "count": total,
        "next": q.page + 1 if q.skip + q.limit < total else None,
        "previous": q.page - 1 if q.page > 1 else None,
        "results": await results,
    }


@root.get("/by_object", response_model=schemas.PaginatedReportsByObject)
async def get_report_list_by_object(q: filters.QueryByObject = Depends()):
    """Query reports grouped by object"""
    total = await db.count_documents(models.Report, q)
    results = db.paginate_documents(models.Report, q)

    return {
        "count": total,
        "next": q.page + 1 if q.skip + q.limit < total else None,
        "previous": q.page - 1 if q.page > 1 else None,
        "results": await results,
    }


@root.get("/csv_reports", response_class=StreamingResponse, responses={200: {"content": {"text/csv": {}}}})
async def download_report_selection(q: filters.QueryByObject = Depends()):
    """Downloads a CSV with object and report information"""
    reports = await db.paginate_documents(models.Report, q)
    reports = pd.DataFrame(reports).drop(columns="users").set_index("object")
    _datetime_to_iso(reports, ["first_date", "last_date"])

    objects = db.query_objects(reports.index.to_list())

    headers = {"Content-Disposition": f"attachment; filename=data.csv"}
    return StreamingResponse(iter(reports.join(objects).to_csv()), media_type="text/csv", headers=headers)


@root.get("/count_by_day", response_model=list[schemas.ReportByDay])
async def count_reports_by_day(q: filters.QueryByDay = Depends()):
    """Query number of reports per day"""
    return await db.read_documents(models.Report, q)


@root.post("/", response_model=schemas.ReportOut, status_code=201)
async def create_new_report(report: schemas.ReportIn = Body(...)):
    """Insert a new report in database. Date, ID and owner are set internally"""
    return await db.create_document(models.Report, report.dict())


@root.get("/{report_id}", response_model=schemas.ReportOut)
async def get_single_report(report_id: str):
    """Retrieve single report based on its ID"""
    document = await db.read_document(models.Report, report_id)
    return _check_exists(document, report_id)


@root.patch("/{report_id}", response_model=schemas.ReportOut)
async def update_existing_report(report_id: str, report: schemas.ReportUpdate = Body(...)):
    """Updates one or more fields of an existing report based on its ID"""
    document = await db.update_document(models.Report, report_id, report.dict(exclude_none=True))
    return _check_exists(document, report_id)


@root.put("/{report_id}", response_model=schemas.ReportOut)
async def replace_existing_report(report_id: str, report: schemas.ReportIn = Body(...)):
    """Updates the full report based on its ID"""
    document = await db.update_document(models.Report, report_id, report.dict())
    return _check_exists(document, report_id)


@root.delete("/{report_id}", status_code=204)
async def delete_report(report_id: str):
    """Deletes existing report based on its ID"""
    document = await db.delete_document(models.Report, report_id)
    _check_exists(document, report_id)
