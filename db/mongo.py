"""MongoDB connection helpers."""

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from config.settings import Settings


settings = Settings()

_client: MongoClient = MongoClient(
    settings.MONGODB_DB_URL,
    tz_aware=True,
    serverSelectionTimeoutMS=5_000,
)
_db: Database = _client[settings.MONGODB_DB_NAME]


def get_database() -> Database:
    """Return the configured MongoDB database."""

    return _db


def get_collection(name: str) -> Collection:
    """Return a collection from the configured database."""

    if not name or not name.strip():
        raise ValueError("Collection name must not be empty.")

    return _db[name]


def ping_database() -> bool:
    """Check that the MongoDB server is reachable."""

    return _client.admin.command("ping").get("ok") == 1.0


def close_database_connection() -> None:
    """Close the shared MongoDB client."""

    _client.close()
