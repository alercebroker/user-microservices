"""CRUD (create, read, update, delete) functions for reports API"""
from db_handler.connection import MongoConnection
from fastapi import encoders

from .filters import BaseQuery, BasePaginatedQuery
from .models import Report, InsertReport


async def create_report(connection: MongoConnection, report: InsertReport) -> dict | None:
    report = Report(**report.dict())
    insert = await connection.insert_one(Report, encoders.jsonable_encoder(report))
    return await connection.find_one(Report, {"_id": insert.inserted_id})


async def read_report(connection: MongoConnection, report_id: str) -> dict | None:
    return await connection.find_one(Report, {"_id": report_id})


async def read_paginated_reports(connection: MongoConnection, q: BasePaginatedQuery) -> dict:
    total = (await connection.aggregate(Report, q.count_pipeline()).to_list(1))[0]["total"]
    results = await connection.aggregate(Report, q.pipeline()).to_list(q.limit)
    return {
        "count": total,
        "next": q.page + 1 if q.skip + q.limit < total else None,
        "previous": q.page - 1 if q.page > 1 else None,
        "results": results
    }


async def read_all_reports(connection: MongoConnection, q: BaseQuery) -> list[dict]:
    total = (await connection.aggregate(Report, q.count_pipeline()).to_list(1))[0]["total"]
    return await connection.aggregate(Report, q.pipeline()).to_list(total)


async def update_report(connection: MongoConnection, report_id: str, report: InsertReport) -> dict | None:
    await connection.update_one(Report, {"_id": report_id}, {"$set": report.dict()})
    return await connection.find_one(Report, {"_id": report_id})


async def delete_report(connection: MongoConnection, report_id: str) -> int:
    delete = await connection.delete_one(Report, {"_id": report_id})
    return delete.deleted_count
