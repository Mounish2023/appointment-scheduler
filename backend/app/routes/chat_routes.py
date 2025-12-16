# # backend/app/routes/chat_routes.py (Updated with AI Agent Integration)

from fastapi import APIRouter, Depends
from ..agents.scheduler_agent.graph import create_dental_appointment_agent
from ..agents.rag_agent.graph import create_rag_agent
import uuid
from fastapi import HTTPException, status
from datetime import datetime
from ..services.conversation_service import ConversationManager
from ..services.user_service import UserService
from pydantic import BaseModel
from uuid import UUID
from ..database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated
from .auth_routes import get_current_active_user
from ..schemas import User

import re
from ..services.gcs_service import GCSService
from ..database import MongoDBClient

router = APIRouter()
conversation_manager = ConversationManager()
user_manager = UserService()
gcs_service = GCSService()
mongo_client = MongoDBClient()
documents_collection = mongo_client.get_collection(collection_name="documents")

CITATION_RE = re.compile(r"\[doc:(?P<doc_id>[^\]|]+)\|p:(?P<page>\d+)\]")

def process_citations(text: str, doc_url_map: dict[str, str], doc_name_map: dict[str, str]) -> tuple[str, list[str]]:
    """
    Replaces [doc:ID|p:Page] with [1], [2] etc.
    Returns processed text and a list of reference strings.
    """
    references = []
    seen_citations = {} # Map (doc_id, page) -> reference number
    
    def repl(m: re.Match) -> str:
        doc_id = m.group("doc_id")
        page = m.group("page")
        
        # If we don't have a URL for this doc, leave it or skip it?
        # Let's leave it as is if not found, or maybe just [?]
        if doc_id not in doc_url_map:
            return m.group(0)

        key = (doc_id, page)
        if key not in seen_citations:
            seen_citations[key] = len(references) + 1
            
            # The doc_url_map contains the base path: /documents/{id}
            # We append the page query param here.
            base_url = doc_url_map[doc_id]
            url = f"{base_url}?page={page}"
            
            name = doc_name_map.get(doc_id, "Document")
            # Simplified reference format: [1] [ULTIMAAX.pdf](/documents/...)
            references.append(f"[{seen_citations[key]}] [{name}]({url})")
            
        ref_num = seen_citations[key]
        # Clickable inline citation: [[1]](/documents/...)
        # We use the same URL for the inline link.
        # Note: We need to reconstruct the URL here because we might have seen this citation before
        # but we don't store the URL in seen_citations.
        # Actually, we can just grab it from doc_url_map again.
        base_url = doc_url_map[doc_id]
        url = f"{base_url}?page={page}"
        
        return f"[[{ref_num}]]({url})"

    processed_text = CITATION_RE.sub(repl, text)
    return processed_text, references

async def enrich_message_with_citations(message_content: str, userid: str) -> str:
    """
    Scans message for citations, fetches doc URLs, and rewrites message with references.
    """
    # 1. Extract doc IDs
    doc_ids = set()
    for m in CITATION_RE.finditer(message_content):
        doc_ids.add(m.group("doc_id"))
    
    if not doc_ids:
        return message_content
    
    # 2. Fetch document metadata
    docs_cursor = documents_collection.find({"id": {"$in": list(doc_ids)}, "userid": userid})
    docs = await docs_cursor.to_list(length=None)
    
    doc_url_map = {}
    doc_name_map = {}
    
    for doc in docs:
        try:
            # Generate PERMANENT frontend link
            # The frontend route is /documents/:id?page=:page
            # We don't need to generate signed URL here, the frontend will request it.
            # We just construct the base URL path for the frontend router.
            # The process_citations function adds the page query param.
            
            # Note: We are constructing a relative path here, assuming the chat 
            # renders this markdwon link effectively.
            # Since the frontend handles the routing, a relative link `/documents/{id}` 
            # should work if clicked within the SPA.
            # If opened in new tab, it also works.
            
            doc_id = doc["id"]
            link = f"/documents/{doc_id}" 
            doc_url_map[doc_id] = link
            doc_name_map[doc_id] = doc.get("filename", "Document")
        except Exception as e:
            print(f"Error generating link for doc {doc.get('id')}: {e}")
            
    # 3. Process citations
    new_text, references = process_citations(message_content, doc_url_map, doc_name_map)
    
    # 4. Append references
    if references:
        new_text += "\n\n**References:**\n" + "\n".join(references)
        
    return new_text


# Pydantic models
class MessageCreate(BaseModel):
    query: str
    document_ids: List[str] = []


class MessageResponse(BaseModel):
    conversationid: str
    document_ids: List[str] = []
    query: str
    response: str
    citations: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionCreate(BaseModel):
    query: str
    document_ids: List[str] = []


class SessionResponse(BaseModel):
    sessionid: str
    userid: str
    conversations: list[MessageResponse]
    document_ids: List[str] = []
    created_at: datetime
    updated_at: datetime  # For ChatGPT-style session titles

    class Config:
        from_attributes = True


@router.post("/session/start", response_model=SessionResponse)
async def start_chat_session(
    session_details: SessionCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """Start a new chat session and send initial greeting."""
    try:
        userid = current_user.userid
        print(userid)
        # Generate a unique thread ID for this conversation
        sessionid = str(uuid.uuid4())

        # Get user data - using current_user directly might be enough if it has all info, 
        # but let's keep user_manager if it fetches more details.
        # Actually user_manager.get_user_by_id might expect string.
        # current_user is likely a Pydantic model from auth_routes.
        
        # We can use current_user directly if it has what we need. 
        # For now, let's assume we need to fetch 'user_dict' for the agent context.
        # If current_user is the Pydantic model User, we can dump it.
        
        user_dict = current_user.model_dump()
        # user_dict = await user_manager.get_user_by_id(db, str(userid)) 
        
        if not user_dict:
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # Prepare user context as a string
        user_context = f"""Current User Information: {user_dict}"""

        # Prepare the input with messages and config
        input_data = {"user_context": user_context, "messages": [{"role": "user", "content": session_details.query}]}

        # Initialize and invoke the agent
        agent = await create_rag_agent()
        result = await agent.ainvoke(input_data)

        print(result)
        response_content = result["messages"][-1].content
        print(response_content)

        # Process citations in the response
        final_response = await enrich_message_with_citations(response_content, str(userid))

        # Save the conversation to MongoDB
        session = await conversation_manager.add_session_conversation(
            userid=str(userid),
            sessionid=sessionid,
            query=session_details.query,
            response=final_response, # Save enriched response? Or raw? 
            # Ideally we save raw and enrich on read, BUT signed URLs expire. 
            # So saving enriched with signed URLs is BAD for long term storage if we want links to work later.
            # However, the current request structure implies we are modifying the "response" field in the return object.
            # If we save the enriched response to DB, the links will expire.
            # WE MUST NOT SAVE ENRICHED RESPONSE TO DB IF IT HAS EXPIRING LINKS.
            # BUT the prompt asks to "replace ... with an actual link".
            # If we want persistent links we need a proxy or we accept they expire.
            # Re-reading plan: "Generate signed URLs... Run linkify... Update message_obj.response".
            # If we update message_obj.response BEFORE saving, we save expiring links.
            # Recommendation: Save RAW response to DB (with [doc:..]), and enrich ONLY on return.
            # But `conversation_manager.add_session_conversation` returns the saved object.
            # So we should call add_session_conversation with RAW, then modify the returned object's response field.
            document_ids=session_details.document_ids
        )
        
        # Enrich the response in the session object before returning to user
        # We need to access the first conversation in the session
        if session.conversations:
             session.conversations[0].response = final_response

        # Return the response with thread_id for future interactions
        return session
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing your request: {str(e)}"
        )


@router.post("/session/{session_id}/message", response_model=MessageResponse)
async def send_message(
    session_id: UUID,
    message_data: MessageCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """Send a message and trigger AI agent processing."""
    try:
        userid = current_user.userid
        # Get session details
        session_details = await conversation_manager.get_session_conversations(
            userid=str(userid), sessionid=str(session_id)
        )
        
        # Get user data
        user_dict = current_user.model_dump()
        
        if not user_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # Prepare user context as a string
        user_context = f"""Current User Information: {user_dict}"""

        # Build chat history
        chat_history = []
        for conv in session_details:
            chat_history.append({"role": "user", "content": conv.query})
            chat_history.append({"role": "assistant", "content": conv.response})
            
        # Prepare input data with user context and current message
        input_data = {
            "user_context": user_context,
            "messages": chat_history + [{"role": "user", "content": message_data.query}]
        }

        # Initialize and invoke the agent
        agent = await create_rag_agent()
        result = await agent.ainvoke(input_data)
        print(result)
        response_content = result["messages"][-1].content

        # Process citations
        final_response = await enrich_message_with_citations(response_content, str(userid))

        # Save RAW conversation to MongoDB
        conversation = await conversation_manager.add_conversation(
            userid=str(userid),
            sessionid=str(session_id),
            query=message_data.query,
            response=response_content, # Save raw content
        )

        # Enrich for return
        conversation.response = final_response

        # Return the response with thread_id for future interactions
        return conversation
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing your request: {str(e)}"
        )


@router.get("/sessions", response_model=List[SessionResponse])
async def get_all_sessions(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Get all chat sessions for the specified user.
    """
    try:
        userid = current_user.userid
        sessions = await conversation_manager.get_all_sessions(userid=str(userid))
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sessions: {str(e)}"
        )


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: UUID, 
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Get all messages for a specific session.
    """
    try:
        userid = current_user.userid
        messages = await conversation_manager.get_session_conversations(
            userid=str(userid), sessionid=str(session_id)
        )
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or no messages available"
            )
            
        # Enrich all messages with fresh links
        for msg in messages:
             msg.response = await enrich_message_with_citations(msg.response, str(userid))
             
        return messages
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving messages: {str(e)}"
        )

