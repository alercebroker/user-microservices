"""CRUD (create, read, update, delete) functions for reports API"""
from db_handler.connection import MongoConnection
from fastapi import encoders

from .filters import BaseQuery, BasePaginatedQuery
from .models import ReportDB, ReportInsert


class DocumentNotFound(ValueError):
    def __init__(self, identifier):
        super().__init__(f"Document not found. ID: {identifier}")


async def create_report(connection: MongoConnection, report: ReportInsert) -> dict:
    report = ReportDB(**report.dict())
    insert = await connection.insert_one(ReportDB, encoders.jsonable_encoder(report))
    return await connection.find_one(ReportDB, {"_id": insert.inserted_id})


async def read_report(connection: MongoConnection, report_id: str) -> dict:
    report = await connection.find_one(ReportDB, {"_id": report_id})
    if report is None:
        raise DocumentNotFound(report_id)
    return report


async def read_paginated_reports(connection: MongoConnection, q: BasePaginatedQuery) -> dict:
    try:
        total, = await connection.aggregate(ReportDB, q.count_pipeline()).to_list(1)
    except ValueError as err:
        # Special case: When the collection is empty total will be an empty list
        if "not enough values to unpack" not in str(err):
            raise
        total = 0
        results = []
    else:
        total = total["total"]
        results = await connection.aggregate(ReportDB, q.pipeline()).to_list(q.limit)
    return {
        "count": total,
        "next": q.page + 1 if q.skip + q.limit < total else None,
        "previous": q.page - 1 if q.page > 1 else None,
        "results": results
    }


async def read_all_reports(connection: MongoConnection, q: BaseQuery) -> list[dict]:
    return [_ async for _ in connection.aggregate(ReportDB, q.pipeline())]


async def update_report(connection: MongoConnection, report_id: str, report: ReportInsert) -> dict:
    await connection.update_one(ReportDB, {"_id": report_id}, {"$set": report.dict(exclude_none=True)})
    report = await connection.find_one(ReportDB, {"_id": report_id})
    if report is None:
        raise DocumentNotFound(report_id)
    return report


async def delete_report(connection: MongoConnection, report_id: str):
    delete = await connection.delete_one(ReportDB, {"_id": report_id})
    if delete.deleted_count == 0:
        raise DocumentNotFound(report_id)
