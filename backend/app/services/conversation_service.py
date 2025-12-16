# 2. CRUD Operations
from ..database import MongoDBClient
from datetime import datetime
import uuid
from ..models.conversation_models import Conversation, Session
from typing import List, Optional


class ConversationManager:
    def __init__(self):
        self.mongo_client = MongoDBClient()
        self.collection = self.mongo_client.get_collection()

    async def add_conversation(
        self, userid: str, sessionid: str, query: str, response: str
    ) -> Conversation:
        """
        Append a new conversation to an existing session.
        """
        conversation = Conversation(
            conversationid=str(uuid.uuid4()),
            query=query,
            response=response,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        result = await self.collection.update_one(
            {"userid": userid, "sessionid": sessionid},
            {
                "$push": {"conversations": conversation.model_dump()},
                "$set": {"updated_at": datetime.now()},
            },
            upsert=False,  # we only append if the session exists
        )

        # Check if no document was modified (session not found)
        if result.matched_count == 0:
            raise ValueError(
                f"No existing session found for userid={userid}, sessionid={sessionid}"
            )

        return conversation

    async def add_session_conversation(
        self, userid: str, sessionid: str, query: str, response: str, document_ids: List[str] = []
    ) -> Session:
        """
        Create a new session document with its first conversation.
        """
        conversation = Conversation(
            conversationid=str(uuid.uuid4()),
            query=query,
            response=response,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Generate title from first query (first 50 characters)
        title = query[:50] + ("..." if len(query) > 50 else "")

        session = Session(
            sessionid=sessionid,
            userid=userid,
            conversations=[conversation],
            title=title,
            document_ids=document_ids,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # $setOnInsert ensures creation if not existing, overwriting if needed
        await self.collection.update_one(
            {"userid": userid, "sessionid": sessionid},
            {"$set": session.model_dump()},
            upsert=True,
        )

        return session

    async def get_session_conversations(
        self, userid: str, sessionid: str
    ) -> List[Conversation]:
        """
        Get all conversations in a session, as a list of Conversation objects.
        """
        result = await self.collection.find_one(
            {"userid": userid, "sessionid": sessionid},
            {"conversations": 1, "_id": 0}
        )

        if not result or "conversations" not in result:
            return []

        return [Conversation(**conv) for conv in result["conversations"]]

    async def get_all_sessions(self, userid: Optional[str] = None) -> List[Session]:
        """
        Get all sessions, optionally filtered by userid.
        """
        query = {"userid": userid} if userid else {}
        cursor = self.collection.find(query)
        results = await cursor.to_list(length=1000)  # Limit to 1000 results

        sessions = []
        for result in results:
            # Build Conversation list safely
            conversations = [
                Conversation(**conv) for conv in result.get("conversations", [])
            ]
            session = Session(
                sessionid=result["sessionid"],
                userid=result["userid"],
                conversations=conversations,
                title=result.get("title"),  # Backwards compatible with existing sessions
                document_ids=result.get("document_ids", []),
                created_at=result.get("created_at", datetime.now()),
                updated_at=result.get("updated_at", datetime.now()),
            )
            sessions.append(session)

        return sessions

    async def get_session_ids(self, userid: Optional[str] = None) -> List[str]:
        """
        Get all unique session IDs, optionally filtered by userid.
        """
        query = {"userid": userid} if userid else {}
        return await self.collection.distinct("sessionid", query)
