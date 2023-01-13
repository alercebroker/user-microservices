from db_handler.connection import MongoConnection
from db_handler.models import Report
from db_handler.utils import DocumentNotFound
from fastapi import encoders

from .filters import BaseQuery, BasePaginatedQuery
from .models import ReportInsert
from .settings import MongoSettings


def get_connection():
    settings = MongoSettings()
    return MongoConnection(settings.dict())


async def create_report(conn: MongoConnection, report: ReportInsert) -> dict:
    report = Report(**report.dict())
    insert = await conn.insert_one(Report, encoders.jsonable_encoder(report))
    return await conn.find_one(Report, {"_id": insert.inserted_id})


async def read_report(conn: MongoConnection, report_id: str) -> dict:
    report = await conn.find_one(Report, {"_id": report_id})
    if report is None:
        raise DocumentNotFound(report_id)
    return report


async def read_paginated_reports(conn: MongoConnection, q: BasePaginatedQuery) -> dict:
    try:
        total, = await conn.aggregate(Report, q.count_pipeline()).to_list(1)
    except ValueError as err:
        # Special case: When the collection is empty total will be an empty list
        if "not enough values to unpack" not in str(err):
            raise
        total = 0
        results = []
    else:
        total = total["total"]
        results = await conn.aggregate(Report, q.pipeline()).to_list(q.limit)
    return {
        "count": total,
        "next": q.page + 1 if q.skip + q.limit < total else None,
        "previous": q.page - 1 if q.page > 1 else None,
        "results": results
    }


async def read_all_reports(conn: MongoConnection, q: BaseQuery) -> list[dict]:
    return [_ async for _ in conn.aggregate(Report, q.pipeline())]


async def update_report(conn: MongoConnection, report_id: str, report: ReportInsert) -> dict:
    await conn.update_one(Report, {"_id": report_id}, {"$set": report.dict(exclude_none=True)})
    report = await conn.find_one(Report, {"_id": report_id})
    if report is None:
        raise DocumentNotFound(report_id)
    return report


async def delete_report(conn: MongoConnection, report_id: str):
    delete = await conn.delete_one(Report, {"_id": report_id})
    if delete.deleted_count == 0:
        raise DocumentNotFound(report_id)
