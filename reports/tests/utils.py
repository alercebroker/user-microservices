import random
from datetime import datetime

from fastapi.testclient import TestClient
from db_handler.utils import ObjectId

from reports.main import app


client = TestClient(app)


def report_factory(**kwargs):
    report = {
        "_id": ObjectId("123456789012345678901234"),
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


def json_converter(report):
    output = {}
    for k, v in report.items():
        if isinstance(v, datetime):
            output[k] = v.isoformat()
        elif isinstance(v, ObjectId):
            output[k] = str(v)
        else:
            output[k] = v
    return output


def create_reports(n=1):
    def oid():
        return ObjectId(''.join(random.choices('01234567890abcdef', k=24)))

    return [report_factory(_id=oid()) for _ in range(n)]


def create_jsons(reports):
    return [json_converter(report) for report in reports]
