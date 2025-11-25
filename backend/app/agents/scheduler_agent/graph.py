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
from typing import Literal, TypedDict, Annotated
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from .tools import tools
from .prompts import SYSTEM_PROMPT
from operator import add
# ============================================
# AGENT STATE
# ============================================





class AgentState(TypedDict):
    """State for the dental appointment booking agent"""
    user_context: Annotated[str, "User context information"]
    messages: Annotated[list, add]



# ============================================
# AGENT NODES
# ============================================

def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """Determine if the agent should continue or end."""
    messages = state["messages"]
    last_message = messages[-1]

    # If there are tool calls, continue to tools node
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    # Otherwise, end
    return "end"


def call_model(state: AgentState):
    """Call the LLM with the current state."""
    messages = state["messages"]
    
    # Add system prompt with current datetime
    system_message = SystemMessage(
        content=SYSTEM_PROMPT.format(
            current_datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z"),
            user_context=state["user_context"]
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
    workflow = StateGraph(AgentState)

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



