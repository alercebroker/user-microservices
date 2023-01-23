import pytest
import pymongo
from pymongo.errors import ServerSelectionTimeoutError


@pytest.fixture(scope="session")
def mongo_service(docker_ip, docker_services):
    """Ensure that mongo service is up and responsive."""
    port = docker_services.port_for("mongo", 27017)
    server = "{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(timeout=30.0, pause=0.1, check=lambda: is_mongo_responsive(server))
    return server


def is_mongo_responsive(url):
    host, port = url.split(":")
    client = pymongo.MongoClient(
        host=host,
        username="user",
        password="password",
        port=int(port),
        serverSelectionTimeoutMS=3000
    )
    try:
        client.server_info()
    except ServerSelectionTimeoutError:
        return False
    finally:
        client.close()
    return True
