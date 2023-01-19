import random
from datetime import date, datetime

from fastapi.testclient import TestClient
from db_handler.utils import ObjectId

from reports.main import app


client = TestClient(app)
random.seed(42)


def random_oid():
    return ObjectId(''.join(random.choices('01234567890abcdef', k=24)))


def report_factory(**kwargs):
    report = {
        "_id": random_oid(),
        "date": datetime.utcnow(),
        "object": "object",
        "solved": False,
        "source": "source",
        "observation": "observation",
        "report_type": "report_type",
        "owner": "owner"
    }
    report.update(kwargs)
    return report


def report_by_object_factory(**kwargs):
    report = {
        "object": "AL" + ''.join(random.choices('1234567890', k=7)),
        "first_date": datetime.utcnow(),
        "last_date": datetime.utcnow(),
        "count": 1,
        "source": ["source"],
        "report_type": ["report_type"],
        "users": ["user"]
    }
    report.update(kwargs)
    return report


def json_converter(report):
    output = {}
    for k, v in report.items():
        if isinstance(v, (datetime, date)):
            output[k] = v.isoformat()
        elif isinstance(v, ObjectId):
            output[k] = str(v)
        else:
            output[k] = v
    return output


def create_reports(n=1):
    return [report_factory() for _ in range(n)]


def create_reports_by_object(n=1):
    return [report_by_object_factory() for _ in range(n)]


def create_jsons(reports):
    return [json_converter(report) for report in reports]
