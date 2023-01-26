from functools import lru_cache

import httpx
import pandas as pd
from astropy.time import Time
from db_handler import MongoConnection, Singleton

from ..settings import MongoSettings, ExtraSettings


class ReportDatabaseConnection(MongoConnection, metaclass=Singleton):
    def __init__(self, db_config, extra_config):
        self._alerts_url = extra_config.alerts_api_url
        super().__init__(db_config)

    def query_objects(self, ids: list[str]) -> pd.DataFrame:
        with httpx.Client() as client:
            objects = client.get(f"{self._alerts_url}/objects", params={"oid": ids, "page_size": len(ids)})
        objects = pd.DataFrame(objects.json()["items"])[["oid", "ndet", "firstmjd", "lastmjd"]]
        objects["firstmjd"] = Time(objects["firstmjd"], format="mjd").to_value("isot")
        objects["lastmjd"] = Time(objects["lastmjd"], format="mjd").to_value("isot")

        mapping = {"oid": "object", "firstmjd": "first_detection", "lastmjd": "last_detection", "ndet": "nobs"}
        return objects.rename(columns=mapping).set_index("object")


@lru_cache
def get_connection() -> ReportDatabaseConnection:
    return ReportDatabaseConnection(MongoSettings().dict(), ExtraSettings())
