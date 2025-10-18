
# Example usage:
# from database import create_document, get_documents, update_document, delete_document
#
# # Create a user
# user_id = create_document("users", {
#     "name": "John Doe",
#     "email": "john@example.com",
#     "age": 30
# })
#
# # Get all users
# users = get_documents("users")
#
# # Get users with filter
# young_users = get_documents("users", {"age": {"$lt": 25}})
#
# # Update a user
# update_document("users", {"email": "john@example.com"}, {"age": 31})
#
# # Delete a user
# delete_document("users", {"email": "john@example.com"})


from pymongo import MongoClient
from datetime import datetime
import os

_client = None
db = None

database_url = os.getenv("DATABASE_URL")
database_name = os.getenv("DATABASE_NAME")

if database_url and database_name:
    _client = MongoClient(database_url)
    db = _client[database_name]

# Helper functions for common database operations
def create_document(collection_name: str, data: dict):
    """Insert a single document with timestamp"""
    if db is None:
        raise Exception("Database not available. Check DATABASE_URL and DATABASE_NAME environment variables.")
    
    data['created_at'] = datetime.utcnow()
    data['updated_at'] = datetime.utcnow()
    
    result = db[collection_name].insert_one(data)
    return str(result.inserted_id)

def get_documents(collection_name: str, filter_dict: dict = None, limit: int = None):
    """Get documents from collection"""
    if db is None:
        raise Exception("Database not available. Check DATABASE_URL and DATABASE_NAME environment variables.")
    
    cursor = db[collection_name].find(filter_dict or {})
    if limit:
        cursor = cursor.limit(limit)
    
    return list(cursor)

def update_document(collection_name: str, filter_dict: dict, update_data: dict):
    """Update a document with timestamp"""
    if db is None:
        raise Exception("Database not available. Check DATABASE_URL and DATABASE_NAME environment variables.")
    
    update_data['updated_at'] = datetime.utcnow()
    
    result = db[collection_name].update_one(filter_dict, {"$set": update_data})
    return result.modified_count > 0

def delete_document(collection_name: str, filter_dict: dict):
    """Delete a document"""
    if db is None:
        raise Exception("Database not initialized. Call enable-database first.")
    
    result = db[collection_name].delete_one(filter_dict)
    return result.deleted_count > 0
