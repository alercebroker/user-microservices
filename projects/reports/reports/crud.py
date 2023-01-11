from db_handler.connection import MongoCollection
from fastapi import encoders

from .filters import QueryByReport, QueryByObject, QueryByDay
from .models import Report, InsertReport, UpdateReport


async def create_report(collection: MongoCollection, report: InsertReport) -> dict | None:
    report = Report(**report.dict())
    insert = await collection.insert_one(encoders.jsonable_encoder(report))
    return await collection.find_one({"_id": insert.inserted_id})


async def get_report(collection: MongoCollection, report_id: str) -> dict | None:
    return await collection.find_one({"_id": report_id})


async def query_reports(collection: MongoCollection, q: QueryByReport) -> list[dict]:
    return await collection.aggregate(q.pipeline()).to_list(q.page_size)


async def query_reports_by_object(collection: MongoCollection, q: QueryByObject) -> list[dict]:
    return await collection.aggregate(q.pipeline()).to_list(q.page_size)


async def count_by_day(collection: MongoCollection, q: QueryByDay) -> list[dict]:
    return await collection.aggregate(q.pipeline()).to_list(q.page_size)


async def update_report(collection: MongoCollection, report_id: str, report: UpdateReport) -> dict | None:
    report = {k: v for k, v in report.dict().items()}
    if len(report):
        await collection.update_one({"_id": report_id}, {"$set": report})
    return await collection.find_one({"_id": report_id})


async def delete_report(collection: MongoCollection, report_id: str) -> int:
    delete = await collection.delete_one({"_id": report_id})
    return delete.deleted_count
