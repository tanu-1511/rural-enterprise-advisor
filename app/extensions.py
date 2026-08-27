"""Simple database abstraction.

Route modules never talk to PyMongo (or the in-memory fallback) directly.
Instead they call `current_app.db.get_collection("name")`, which returns an
object with a small, consistent interface:

    insert_one(document) -> id
    find_one(id) -> document or None
    find_all() -> list of documents
    update_one(id, updates) -> bool
    delete_one(id) -> bool

Every stored document gets a string "id" field (a uuid4 hex string). This
keeps the interface identical whether the data lives in MongoDB or in a
plain Python dictionary, and avoids exposing MongoDB's internal ObjectId
type to the rest of the application.
"""

import uuid


class InMemoryCollection:
    """A minimal stand-in for a MongoDB collection.

    Used automatically during tests, and usable for local development
    when MongoDB is not running (see USE_IN_MEMORY_DB in config.py).
    """

    def __init__(self):
        self._documents: dict[str, dict] = {}

    def insert_one(self, document: dict) -> str:
        doc = dict(document)
        doc_id = uuid.uuid4().hex
        doc["id"] = doc_id
        self._documents[doc_id] = doc
        return doc_id

    def find_one(self, doc_id: str) -> dict | None:
        doc = self._documents.get(doc_id)
        return dict(doc) if doc else None

    def find_all(self) -> list[dict]:
        return [dict(doc) for doc in self._documents.values()]

    def update_one(self, doc_id: str, updates: dict) -> bool:
        if doc_id not in self._documents:
            return False
        self._documents[doc_id].update(updates)
        return True

    def delete_one(self, doc_id: str) -> bool:
        return self._documents.pop(doc_id, None) is not None


class MongoCollection:
    """Wraps a PyMongo collection behind the same interface as
    InMemoryCollection, so route code does not need to know which
    backend is active.
    """

    def __init__(self, collection):
        self._collection = collection

    def insert_one(self, document: dict) -> str:
        doc = dict(document)
        doc_id = uuid.uuid4().hex
        doc["id"] = doc_id
        self._collection.insert_one(doc)
        return doc_id

    def find_one(self, doc_id: str) -> dict | None:
        doc = self._collection.find_one({"id": doc_id})
        if doc is not None:
            doc.pop("_id", None)
        return doc

    def find_all(self) -> list[dict]:
        docs = list(self._collection.find())
        for doc in docs:
            doc.pop("_id", None)
        return docs

    def update_one(self, doc_id: str, updates: dict) -> bool:
        result = self._collection.update_one({"id": doc_id}, {"$set": updates})
        return result.matched_count > 0

    def delete_one(self, doc_id: str) -> bool:
        result = self._collection.delete_one({"id": doc_id})
        return result.deleted_count > 0


class Database:
    """Picks a backend (MongoDB or in-memory) and hands out collections."""

    def __init__(self, use_in_memory: bool, mongo_uri: str | None = None):
        self._use_in_memory = use_in_memory
        self._collections: dict[str, object] = {}
        self._mongo_db = None

        if not use_in_memory:
            # Imported lazily so the app (and tests, which use the
            # in-memory backend) do not require pymongo to be installed
            # unless MongoDB is actually being used.
            from pymongo import MongoClient

            client = MongoClient(mongo_uri)
            self._mongo_db = client.get_default_database()

    def get_collection(self, name: str):
        if name in self._collections:
            return self._collections[name]

        if self._use_in_memory:
            collection = InMemoryCollection()
        else:
            collection = MongoCollection(self._mongo_db[name])

        self._collections[name] = collection
        return collection
