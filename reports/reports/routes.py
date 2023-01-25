import httpx
import pandas as pd
from astropy.time import Time
from db_handler import DocumentNotFound
from fastapi import APIRouter, Body, Depends
from fastapi.responses import StreamingResponse

from . import database, filters, schemas
from .database import models


root = APIRouter()


def _check_exists(document, oid):
    if document is None:
        raise DocumentNotFound(oid)
    return document


@root.get("/", response_model=schemas.PaginatedReports)
async def get_report_list(q: filters.QueryByReport = Depends()):
    """Query reports"""
    total = await database.get_connection().count_documents(models.Report, q)
    results = database.get_connection().paginate_documents(models.Report, q)

    return {
        "count": total,
        "next": q.page + 1 if q.skip + q.limit < total else None,
        "previous": q.page - 1 if q.page > 1 else None,
        "results": await results,
    }


@root.get("/by_object", response_model=schemas.PaginatedReportsByObject)
async def get_report_list_by_object(q: filters.QueryByObject = Depends()):
    """Query reports grouped by object"""
    total = await database.get_connection().count_documents(models.Report, q)
    results = database.get_connection().paginate_documents(models.Report, q)

    return {
        "count": total,
        "next": q.page + 1 if q.skip + q.limit < total else None,
        "previous": q.page - 1 if q.page > 1 else None,
        "results": await results,
    }


@root.get("/csv_reports", response_class=StreamingResponse)
async def get_reports_as_csv(q: filters.QueryByObject = Depends()):
    """Query reports grouped by object"""
    reports = await database.get_connection().paginate_documents(models.Report, q)
    reports = pd.DataFrame(reports["results"]).drop(columns="users").set_index("object")
    reports["first_date"].map(lambda x: x.isoformat(timespec="milliseconds"))
    reports["last_date"].map(lambda x: x.isoformat(timespec="milliseconds"))

    url = "https://api.alerce.online/alerts/v1/objects"
    with httpx.Client() as client:
        objects = client.get(url, params={"oid": reports.index.to_list(), "page_size": q.page_size})
    objects = pd.DataFrame(objects.json()["items"])[["oid", "ndet", "firstmjd", "lastmjd"]]
    objects["firstmjd"] = Time(objects["firstmjd"], format="mjd").to_value("isot")
    objects["lastmjd"] = Time(objects["lastmjd"], format="mjd").to_value("isot")

    mapping = {"oid": "object", "firstmjd": "first_detection", "lastmjd": "last_detection", "ndet": "nobs"}
    objects = objects.rename(columns=mapping).set_index("object")

    headers = {"Content-Disposition": f"attachment; filename=data.csv"}
    return StreamingResponse(iter(objects.join(reports).to_csv()), media_type="text/csv", headers=headers)


@root.get("/count_by_day", response_model=list[schemas.ReportByDay])
async def count_reports_by_day(q: filters.QueryByDay = Depends()):
    """Query number of reports per day"""
    return await database.get_connection().read_documents(models.Report, q)


@root.post("/", response_model=schemas.ReportOut, status_code=201)
async def create_new_report(report: schemas.ReportIn = Body(...)):
    """Insert a new report in database. Date, ID and owner are set internally"""
    return await database.get_connection().create_document(models.Report, report.dict())


@root.get("/{report_id}", response_model=schemas.ReportOut)
async def get_single_report(report_id: str):
    """Retrieve single report based on its ID"""
    document = await database.get_connection().read_document(models.Report, report_id)
    return _check_exists(document, report_id)


@root.patch("/{report_id}", response_model=schemas.ReportOut)
async def update_existing_report(report_id: str, report: schemas.ReportUpdate = Body(...)):
    """Updates one or more fields of an existing report based on its ID"""
    document = await database.get_connection().update_document(models.Report, report_id, report.dict(exclude_none=True))
    return _check_exists(document, report_id)


@root.put("/{report_id}", response_model=schemas.ReportOut)
async def replace_existing_report(report_id: str, report: schemas.ReportIn = Body(...)):
    """Updates the full report based on its ID"""
    document = await database.get_connection().update_document(models.Report, report_id, report.dict())
    return _check_exists(document, report_id)


@root.delete("/{report_id}", status_code=204)
async def delete_report(report_id: str):
    """Deletes existing report based on its ID"""
    document = await database.get_connection().delete_document(models.Report, report_id)
    _check_exists(document, report_id)
