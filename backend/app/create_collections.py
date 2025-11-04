from pymongo import MongoClient
from pymongo.errors import CollectionInvalid

def create_conversations_collection():
    """Create Users collection with schema validation"""
    client = MongoClient("mongodb://localhost:27017")
    db = client["conversations_db"]
    
    # Define schema validator
    conversations_schema = {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["userid", "sessionid", "created_at", "conversations", "updated_at"],
                "properties": {
                    "userid": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "sessionid": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "created_at": {
                        "bsonType": "date",
                        "description": "must be a date and is required"
                    },
                    "updated_at": {
                        "bsonType": "date",
                        "description": "must be a date and is required"
                    },
                    "conversations": {
                        "bsonType": "array",
                        "description": "must be an array and is required",
                        "items": {
                            "bsonType": "object",
                            "required": ["conversationid", "query", "response", "created_at", "updated_at"],
                            "properties": {
                                "conversationid": {
                                    "bsonType": "string",
                                    "description": "must be a string and is required"
                                },
                                "query": {
                                    "bsonType": "string",
                                    "description": "must be a string and is required"
                                },
                                "response": {
                                    "bsonType": "string",
                                    "description": "must be a string and is required"
                                },
                                "created_at": {
                                    "bsonType": "date",
                                    "description": "must be a date and is required"
                                },
                                "updated_at": {
                                    "bsonType": "date",
                                    "description": "must be a date and is required"
                                }
                            }
                        }
                    }
                }
            }
        },
        "validationLevel": "strict",
        "validationAction": "error"
    }
    
    # Create collection with validation
    try:
        db.create_collection("conversations", **conversations_schema)
        print("conversations collection created successfully with schema validation")
    except CollectionInvalid as e:
        # If collection exists, modify it to add validation
        if "already exists" in str(e):
            db.command("collMod", "conversations", validator=conversations_schema["validator"])
            print("Schema validation added to existing conversations collection")
        else:
            print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        client.close()

