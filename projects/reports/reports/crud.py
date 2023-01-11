from db_handler.connection import MongoCollection
from fastapi import encoders

from .filters import QueryByReport, QueryByObject
from .models import Report, InsertReport, UpdateReport, ReportByObject


async def get_report(collection: MongoCollection, report_id: str) -> dict | None:
    return await collection.find_one({"_id": report_id})


async def query_reports(collection: MongoCollection, q: QueryByReport) -> list[dict]:
    limit = q.page_size
    skip = (q.page - 1) * limit
    return await collection.find(q.query()).sort(q.sort()).skip(skip).limit(limit).to_list(limit)


async def create_report(collection: MongoCollection, report: InsertReport) -> dict | None:
    report = Report(**report.dict())
    insert = await collection.insert_one(encoders.jsonable_encoder(report))
    return await collection.find_one({"_id": insert.inserted_id})


async def update_report(collection: MongoCollection, report_id: str, report: UpdateReport) -> dict | None:
    report = {k: v for k, v in report.dict().items()}
    if len(report):
        await collection.update_one({"_id": report_id}, {"$set": report})
    return await collection.find_one({"_id": report_id})


async def delete_report(collection: MongoCollection, report_id: str) -> int:
    delete = await collection.delete_one({"_id": report_id})
    return delete.deleted_count
