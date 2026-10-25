"""Persistence services for chat conversations."""

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from pymongo import DESCENDING, ReturnDocument

from db.mongo import get_collection


conversations = get_collection("conversations")


# ---------- Helpers ----------

def now_utc() -> datetime:
    """Return the current timezone-aware UTC datetime."""

    return datetime.now(timezone.utc)


def create_new_conversation_id() -> str:
    """Create a unique identifier for a conversation."""

    return str(uuid4())


# ---------- Core Services ----------

def create_new_conversation(
    title: Optional[str] = None,
    role: Optional[str] = None,
    content: Optional[str] = None,
) -> str:
    """Create a conversation and optionally add its first message."""

    conv_id = create_new_conversation_id()
    timestamp = now_utc()

    document: dict[str, Any] = {
        "_id": conv_id,
        "title": title or "Untitled Conversation",
        "messages": [],
        "last_interacted": timestamp,
    }

    if role and content:
        document["messages"].append(
            {
                "role": role,
                "content": content,
                "ts": timestamp,
            }
        )

    conversations.insert_one(document)
    return conv_id


def add_message(conv_id: str, role: str, content: str) -> bool:
    """Append a message to an existing conversation."""

    timestamp = now_utc()

    result = conversations.update_one(
        {"_id": conv_id},
        {
            "$push": {
                "messages": {
                    "role": role,
                    "content": content,
                    "ts": timestamp,
                }
            },
            "$set": {"last_interacted": timestamp},
        },
    )

    return result.matched_count == 1


def get_conversation(conv_id: str) -> Optional[dict[str, Any]]:
    """Return a conversation and update its last-interacted timestamp."""

    return conversations.find_one_and_update(
        {"_id": conv_id},
        {"$set": {"last_interacted": now_utc()}},
        return_document=ReturnDocument.AFTER,
    )


def get_all_conversations() -> dict[str, str]:
    """Return conversation IDs and titles, newest interaction first."""

    cursor = conversations.find({}).sort("last_interacted", DESCENDING)
    return {document["_id"]: document["title"] for document in cursor}
