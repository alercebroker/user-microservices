from fastapi import FastAPI, Body, Depends, HTTPException

from . import crud
from .database import connection
from .filters import QueryByReport, QueryByObject, QueryByDay
from .models import Report, InsertReport, UpdateReport, ByObjectReport, ByDayReport


app = FastAPI()


@app.on_event("startup")
async def startup():
    await connection.connect()


@app.on_event("shutdown")
async def shutdown():
    await connection.close()


@app.get("/", response_model=list[Report], response_description="Report list", response_model_by_alias=False)
async def get_report_list(q: QueryByReport = Depends()):
    return await crud.query_reports(connection.collection, q)


@app.get("/by_object", response_model=list[ByObjectReport], response_description="Report list grouped by object", response_model_by_alias=False)
async def get_report_list_by_object(q: QueryByObject = Depends()):
    return await crud.query_reports_by_object(connection.collection, q)


@app.get("/count_by_day", response_model=list[ByDayReport], response_description="Count of reports by day", response_model_by_alias=False)
async def count_reports_by_day(q: QueryByDay = Depends()):
    return await crud.count_by_day(connection.collection, q)


@app.post("/", response_model=Report, response_description="Created report", status_code=201, response_model_by_alias=False)
async def create_new_report(report: InsertReport = Body(...)):
    return await crud.create_report(connection.collection, report)


@app.get("/{report_id}", response_model=Report, response_description="Requested report", response_model_by_alias=False)
async def get_single_report(report_id: str):
    """Retrieve single report based on its ID"""
    report = await crud.get_report(connection.collection, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report ID {report_id} not found")
    return report


@app.patch("/{report_id}", response_model=Report, response_description="Report updated", response_model_by_alias=False)
async def update_existing_report(report_id: str, report: UpdateReport = Body(...)):
    """Updates an existing report based on its ID"""
    report = await crud.update_report(connection.collection, report_id, report)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report ID {report_id} not found")
    return report


@app.delete("/{report_id}", response_description="Report deleted", status_code=204)
async def delete_report(report_id: str):
    """Deletes existing report based on its ID"""
    deleted = await crud.delete_report(connection.collection, report_id)
    if deleted:
        return
    raise HTTPException(status_code=404, detail=f"Report ID {report_id} not found")
