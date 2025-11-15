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
from .prompts import SYSTEM_PROMPT

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



