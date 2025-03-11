from pymongo import MongoClient
from datetime import datetime
import uuid

client = MongoClient("mongodb://localhost:27017")
db = client["drug_documents"] 
chat_sessions_collection = db["chat_sessions"]  


def create_session():
    """
    Creates a new session document with a default assistant message.
    Returns the new session's ID.
    """
    session_id = str(uuid.uuid4())
    session_doc = {
        "_id": session_id,
        "messages": [
            {
                "role": "assistant",
                "content": "How can I assist you today?",
                "timestamp": datetime.utcnow()
            }
        ],
        "drug_name": session_id,
        "created_at": datetime.utcnow()
    }
    chat_sessions_collection.insert_one(session_doc)
    return session_id

def get_session(session_id):
    """
    Retrieves a session document by its session_id.
    """
    session_doc = chat_sessions_collection.find_one({"_id": session_id})
    return session_doc

def add_message(session_id, message):
    """
    Adds a new message to the session's messages array.
    The message should be a dictionary with keys: 'role' and 'content'.
    """
    # Add a timestamp to the message
    message["timestamp"] = datetime.utcnow()
    result = chat_sessions_collection.update_one(
        {"_id": session_id},
        {"$push": {"messages": message}}
    )
    return result.modified_count > 0

def list_sessions():
    """
    Returns a list of all session IDs.
    """
    sessions = chat_sessions_collection.find({}, {"_id": 1})
    return [doc["_id"] for doc in sessions]


def delete_session(session_id: str) -> bool:
    """
    Deletes the session document by its _id.
    Returns True if a document was deleted, False otherwise.
    """
    result = chat_sessions_collection.delete_one({"_id": session_id})
    return result.deleted_count > 0


def update_drug_name(session_id: str, drug_name: str) -> bool:
    result = chat_sessions_collection.update_one(
        {"_id": session_id},
        {"$set": {"drug_name": drug_name}}
    )
    return result.modified_count > 0