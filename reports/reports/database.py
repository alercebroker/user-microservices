from db_handler.connection import MongoConnection
from db_handler.utils import DocumentNotFound, ObjectId

from .filters import BaseQuery, BasePaginatedQuery
from .models import Report, ReportIn
from .settings import MongoSettings


connection = MongoConnection(MongoSettings())


async def create_report(report: ReportIn) -> dict:
    report = Report(**report.dict())
    insert = await connection.insert_one(Report, report.dict(by_alias=True))
    return await connection.find_one(Report, {"_id": insert.inserted_id})


async def read_report(report_id: str) -> dict:
    report = await connection.find_one(Report, {"_id": ObjectId(report_id)})
    if report is None:
        raise DocumentNotFound(report_id)
    return report


async def read_paginated_reports(q: BasePaginatedQuery) -> dict:
    try:
        total, = await connection.aggregate(Report, q.count_pipeline()).to_list(1)
    except ValueError as err:
        # Special case: When the collection is empty total will be an empty list
        if "not enough values to unpack" not in str(err):
            raise
        total = 0
        results = []
    else:
        total = total["total"]
        results = await connection.aggregate(Report, q.pipeline()).to_list(q.limit)
    return {
        "count": total,
        "next": q.page + 1 if q.skip + q.limit < total else None,
        "previous": q.page - 1 if q.page > 1 else None,
        "results": results
    }


async def read_all_reports(q: BaseQuery) -> list[dict]:
    return [_ async for _ in connection.aggregate(Report, q.pipeline())]


async def update_report(report_id: str, report: ReportIn) -> dict:
    update = {"$set": report.dict(exclude_none=True)}
    report = await connection.find_one_and_update(Report, {"_id": ObjectId(report_id)}, update, return_document=True)
    if report is None:
        raise DocumentNotFound(report_id)
    return report


async def delete_report(report_id: str):
    report = await connection.find_one_and_delete(Report, {"_id": ObjectId(report_id)})
    if report is None:
        raise DocumentNotFound(report_id)
