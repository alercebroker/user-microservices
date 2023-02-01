from functools import lru_cache

import httpx
import pandas as pd
from db_handler import MongoConnection, Singleton

from ..settings import get_settings


class ReportDatabaseConnection(MongoConnection, metaclass=Singleton):
    def __init__(self, **kwargs):
        self._alerts_url = kwargs.pop("alerts_api_url")
        super().__init__(**kwargs.pop("mongodb"))

    def query_objects(self, ids: list[str]) -> pd.DataFrame:
        with httpx.Client() as client:
            objects = client.get(f"{self._alerts_url}/objects", params={"oid": ids, "page_size": len(ids)})
        if objects.is_error:
            self.logger.error(f"Cannot connect to {self._alerts_url} (error {objects.status_code})")
            raise ConnectionError("Cannot connect to ALeRCE alerts API")
        objects = pd.DataFrame(objects.json()["items"])[["oid", "ndet", "firstmjd", "lastmjd"]].drop_duplicates()

        mapping = {"oid": "object", "firstmjd": "first_detection", "lastmjd": "last_detection", "ndet": "nobs"}
        return objects.rename(columns=mapping).set_index("object")


@lru_cache
def get_connection() -> ReportDatabaseConnection:
    return ReportDatabaseConnection(**get_settings().dict())
