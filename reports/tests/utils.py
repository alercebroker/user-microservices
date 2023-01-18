from datetime import datetime

from fastapi.testclient import TestClient

from reports.main import app


client = TestClient(app)


def report_factory(**kwargs):
    report = {
        "_id": "1",
        "date": datetime(2023, 1, 1, 0, 0, 0),
        "object": "object",
        "solved": False,
        "source": "source",
        "observation": "observation",
        "report_type": "report_type",
        "owner": "owner"
    }
    report.update(kwargs)
    return report


def json_factory(report):
    return {k: v.isoformat() if isinstance(v, datetime) else v for k, v in report.items()}


def create_reports(n=1):
    return [report_factory(_id=str(i)) for i in range(n)]


def create_jsons(reports):
    return [json_factory(report) for report in reports]
