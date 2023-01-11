from fastapi import FastAPI, Body, Depends, HTTPException

from . import crud
from .database import connection
from .filters import QueryByReport
from .models import Report, InsertReport, UpdateReport


app = FastAPI()


@app.on_event("startup")
async def startup():
    await connection.connect()


@app.on_event("shutdown")
async def shutdown():
    await connection.close()


@app.get("/", response_model=list[Report], response_description="Report list")
async def get_report_list(q: QueryByReport = Depends()):
    return await crud.query_reports(connection.collection, q)


@app.post("/", response_model=Report, response_description="Created report", status_code=201)
async def create_new_report(report: InsertReport = Body(...)):
    return await crud.create_report(connection.collection, report)


@app.get("/{report_id}", response_model=Report, response_description="Requested report")
async def get_single_report(report_id: str):
    """Retrieve single report based on its ID"""
    report = await crud.get_report(connection.collection, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report ID {report_id} not found")
    return report


@app.patch("/{report_id}", response_model=Report, response_description="Report updated")
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
