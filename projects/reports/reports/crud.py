from db_handler.connection import MongoConnection
from fastapi import encoders

from .filters import QueryByReport, QueryByObject, QueryByDay
from .models import Report, InsertReport, UpdateReport


async def create_report(connection: MongoConnection, report: InsertReport) -> dict | None:
    report = Report(**report.dict())
    insert = await connection.insert_one(Report, encoders.jsonable_encoder(report))
    return await connection.find_one(Report, {"_id": insert.inserted_id})


async def get_report(connection: MongoConnection, report_id: str) -> dict | None:
    return await connection.find_one(Report, {"_id": report_id})


async def query_reports(connection: MongoConnection, q: QueryByReport) -> list[dict]:
    return await connection.aggregate(Report, q.pipeline()).to_list(q.page_size)


async def query_reports_by_object(connection: MongoConnection, q: QueryByObject) -> list[dict]:
    return await connection.aggregate(Report, q.pipeline()).to_list(q.page_size)


async def count_by_day(connection: MongoConnection, q: QueryByDay) -> list[dict]:
    return await connection.aggregate(Report, q.pipeline()).to_list(q.page_size)


async def update_report(connection: MongoConnection, report_id: str, report: UpdateReport) -> dict | None:
    report = {k: v for k, v in report.dict().items()}
    if len(report):
        await connection.update_one(Report, {"_id": report_id}, {"$set": report})
    return await connection.find_one(Report, {"_id": report_id})


async def delete_report(connection: MongoConnection, report_id: str) -> int:
    delete = await connection.delete_one(Report, {"_id": report_id})
    return delete.deleted_count
