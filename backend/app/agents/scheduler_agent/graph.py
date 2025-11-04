"""
LangGraph AI Agent for Dental Appointment Booking System

This agent can:
- Answer questions about providers, services, and appointments
- Check availability and book appointments
- Generate SQL queries from natural language
- Execute queries safely
- Format results in natural language

Built with LangGraph and follows the ReAct pattern with custom tool nodes.
"""

import os
from typing import Literal, TypedDict, Annotated
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_community.utilities import SQLDatabase

from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from .tools import tools

# ============================================
# AGENT STATE
# ============================================

class AgentState(TypedDict):
    """State for the dental appointment booking agent"""
    messages: Annotated[list, "The conversation history"]
    schema_context: Annotated[str, "Database schema information"]
    query_result: Annotated[str, "SQL query execution result"]
    current_step: Annotated[str, "Current step in the workflow"]





# ============================================
# SYSTEM PROMPT
# ============================================

SYSTEM_PROMPT = """You are an intelligent AI assistant for a dental appointment booking system.

Your role is to help patients and staff with:
1. Finding information about dentists, hygienists, and their specialties
2. Checking what dental services are available
3. Finding available appointment slots
4. Booking appointments
5. Answering questions about existing appointments

You have access to a PostgreSQL database with these tables:
- users (patients with contact info, insurance, medical history)
- service_providers (dentists and hygienists)
- services (dental procedures like cleanings, fillings, etc.)
- appointments (scheduled appointments)
- availability_rules (when providers are available)
- recurring_patterns (for recurring appointments)
- appointment_exceptions (cancelled/rescheduled appointments)

WORKFLOW:
When a user asks a question, follow these steps:

1. **Understand the question**: Determine what information is needed
2. **Get schema**: If needed, retrieve relevant table schemas
3. **Generate query**: Create a SQL query to get the data
4. **Validate query**: Check the query for errors and security issues
5. **Execute query**: Run the query on the database
6. **Format results**: Convert results into a natural language response

For appointment booking requests:
1. Check availability first
2. Confirm all details with the user
3. Only book after explicit user confirmation

For appointment operations:
- Use create_appointment() to book new appointments
- Use update_appointment() to reschedule
- Use cancel_appointment() to cancel
- Use confirm_appointment() to confirm scheduled appointments
- Always confirm with the user before creating/modifying appointments

Never try to use execute_sql_query() for INSERT, UPDATE, or DELETE operations.
Use the specialized write tools instead.


IMPORTANT RULES:
- NEVER execute INSERT, UPDATE, DELETE, or DROP queries without explicit confirmation
- Always store appointment times in UTC
- Check for scheduling conflicts before booking
- Be conversational and friendly
- If you're unsure, ask clarifying questions
- Protect patient privacy - don't share sensitive information

Current date and time: {current_datetime}
"""


# ============================================
# AGENT NODES
# ============================================

def should_continue(state: MessagesState) -> Literal["tools", "end"]:
    """Determine if the agent should continue or end."""
    messages = state["messages"]
    last_message = messages[-1]

    # If there are tool calls, continue to tools node
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    # Otherwise, end
    return "end"


def call_model(state: MessagesState):
    """Call the LLM with the current state."""
    messages = state["messages"]

    # Add system prompt with current datetime
    system_message = SystemMessage(
        content=SYSTEM_PROMPT.format(
            current_datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
        )
    )

    # Initialize LLM with tools
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    # Invoke the model
    response = llm_with_tools.invoke([system_message] + messages)

    return {"messages": [response]}


# ============================================
# BUILD THE GRAPH
# ============================================

async def create_dental_appointment_agent():
    """Create the LangGraph agent for dental appointment booking."""

    # Initialize the graph
    workflow = StateGraph(MessagesState)

    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))

    # Set the entry point
    workflow.set_entry_point("agent")

    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )

    # Add edge from tools back to agent
    workflow.add_edge("tools", "agent")

    # Compile with memory
    # memory = MemorySaver()
    app = workflow.compile()

    return app



