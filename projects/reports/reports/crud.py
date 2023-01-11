from db_handler.connection import MongoConnection
from fastapi import encoders

from .filters import BaseQuery
from .models import Report, InsertReport


async def create_report(connection: MongoConnection, report: InsertReport) -> dict | None:
    report = Report(**report.dict())
    insert = await connection.insert_one(Report, encoders.jsonable_encoder(report))
    return await connection.find_one(Report, {"_id": insert.inserted_id})


async def read_report(connection: MongoConnection, report_id: str) -> dict | None:
    return await connection.find_one(Report, {"_id": report_id})


async def read_paginated_reports(connection: MongoConnection, q: BaseQuery) -> dict:
    total, = await connection.aggregate(Report, q.pipeline(paginate=False, count=True)).to_list(1)
    results = await connection.aggregate(Report, q.pipeline(paginate=True, count=False)).to_list(q.page_size)
    return {
        "count": total["total"],
        "next": q.page + 1 if q.skip() + q.limit() < total["total"] else None,
        "previous": q.page - 1 if q.page > 1 else None,
        "results": results
    }


async def update_report(connection: MongoConnection, report_id: str, report: InsertReport) -> dict | None:
    await connection.update_one(Report, {"_id": report_id}, {"$set": report.dict()})
    return await connection.find_one(Report, {"_id": report_id})


async def delete_report(connection: MongoConnection, report_id: str) -> int:
    delete = await connection.delete_one(Report, {"_id": report_id})
    return delete.deleted_count
