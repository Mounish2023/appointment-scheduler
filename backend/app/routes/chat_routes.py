# # backend/app/routes/chat_routes.py (Updated with AI Agent Integration)

from fastapi import APIRouter, Depends
from ..agents.scheduler_agent.graph import create_dental_appointment_agent
import uuid
from fastapi import HTTPException, status
from datetime import datetime
from ..services.conversation_service import ConversationManager
from ..services.user_service import UserService
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from langchain.schema import AIMessage, HumanMessage
# from langchain_community.utilities import SQLDatabase
# DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/dental_appointment_db"
# db = SQLDatabase.from_uri(DATABASE_URL)
import json
from ..models.dental_appointment_models import User
from ..database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

# db = Depends(get_db)

router = APIRouter()
conversation_manager = ConversationManager()
user_manager = UserService()

# Pydantic models
class MessageCreate(BaseModel):
    query: str


class MessageResponse(BaseModel):
    conversationid: str
    query: str
    response: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionCreate(BaseModel):
    query: str


class SessionResponse(BaseModel):
    sessionid: str
    userid: str
    conversations: list[MessageResponse]
    created_at: datetime
    updated_at: datetime  # For ChatGPT-style session titles

    class Config:
        from_attributes = True


@router.post("/session/start", response_model=SessionResponse)
async def start_chat_session(userid: UUID, session_details: SessionCreate):
    """Start a new chat session and send initial greeting."""
    try:
        # Generate a unique thread ID for this conversation
        sessionid = str(uuid.uuid4())

        # Prepare the input with messages and config
        input_data = {"messages": [{"role": "user", "content": session_details.query}]}

        # Initialize and invoke the agent
        agent = await create_dental_appointment_agent()
        result = await agent.ainvoke(input_data)

        print(result)
        response_content = result["messages"][-1].content
        print(response_content)
        # Save the conversation to MongoDB
        session = await conversation_manager.add_session_conversation(
            userid=str(userid),
            sessionid=sessionid,
            query=session_details.query,
            response=response_content
        )
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
    userid: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Send a message and trigger AI agent processing."""
    try:
        # Get session details
        session_details = await conversation_manager.get_session_conversations(
            userid=str(userid), sessionid=str(session_id)
        )
        
        # Get user data
        user_dict = await user_manager.get_user_by_id(db, str(userid))
        if not user_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # Prepare user context as a string
        user_context = f"""User Information:
        - Name: {user_dict.get('full_name')}
        - Email: {user_dict.get('email')}
        - Phone: {user_dict.get('phone', 'Not provided')}
        - Insurance: {user_dict.get('insurance_provider', 'Not provided')}
        - Date of Birth: {user_dict.get('date_of_birth', 'Not provided')}"""

        # Build chat history
        chat_history = []
        for conv in session_details:
            chat_history.append({"role": "user", "content": conv.query})
            chat_history.append({"role": "assistant", "content": conv.response})
            
        # Prepare input data with user context and current message
        input_data = {
            "messages": chat_history + [
                {"role": "system", "content": user_context},
                {"role": "user", "content": message_data.query}
            ]
        }

        # Initialize and invoke the agent
        agent = await create_dental_appointment_agent()
        result = await agent.ainvoke(input_data)
        print(result)
        response_content = result["messages"][-1].content

        # Save the conversation to MongoDB
        conversation = await conversation_manager.add_conversation(
            userid=str(userid),
            sessionid=str(session_id),
            query=message_data.query,
            response=response_content,
        )

        # Return the response with thread_id for future interactions
        return conversation
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing your request: {str(e)}"
        )


@router.get("/sessions", response_model=List[SessionResponse])
async def get_all_sessions(userid: UUID):
    """
    Get all chat sessions for the specified user.
    """
    try:
        sessions = await conversation_manager.get_all_sessions(userid=str(userid))
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sessions: {str(e)}"
        )


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(session_id: UUID, userid: UUID):
    """
    Get all messages for a specific session.
    """
    try:
        messages = await conversation_manager.get_session_conversations(
            userid=str(userid), sessionid=str(session_id)
        )
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or no messages available"
            )
        return messages
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving messages: {str(e)}"
        )

