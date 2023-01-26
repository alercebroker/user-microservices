import httpx
import pandas as pd
from astropy.time import Time
from db_handler import MongoConnection, Singleton

from ..settings import get_settings


class ReportDatabaseConnection(MongoConnection, metaclass=Singleton):
    def __init__(self, **kwargs):
        self._alerts_url = kwargs.pop("alerts_api_url")
        super().__init__(**kwargs.pop("mongodb"))

    @staticmethod
    def _mjd_to_iso(dataframe: pd.DataFrame, fields: str | list[str]):
        if isinstance(fields, str):
            fields = [fields]
        for field in fields:
            dataframe[field] = Time(dataframe[field], format="mjd").to_value("isot")

    def query_objects(self, ids: list[str]) -> pd.DataFrame:
        with httpx.Client() as client:
            objects = client.get(f"{self._alerts_url}/objects", params={"oid": ids, "page_size": len(ids)})
        objects = pd.DataFrame(objects.json()["items"])[["oid", "ndet", "firstmjd", "lastmjd"]]
        self._mjd_to_iso(objects, ["firstmjd", "lastmjd"])

        mapping = {"oid": "object", "firstmjd": "first_detection", "lastmjd": "last_detection", "ndet": "nobs"}
        return objects.rename(columns=mapping).set_index("object")


db = ReportDatabaseConnection(**get_settings().dict())
