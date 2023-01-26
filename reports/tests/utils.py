import random
from datetime import date, datetime

from bson import ObjectId
from fastapi.testclient import TestClient

from reports.main import app
from reports.utils import REPORT_TYPES


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
        "report_type": random.choice(REPORT_TYPES),
        "owner": "owner"
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
