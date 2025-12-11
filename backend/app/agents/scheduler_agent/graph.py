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
# from langgraph.prebuilt import ToolNode
from .tools import tools, tools_by_name
from .prompts import SYSTEM_PROMPT
from operator import add
from langchain_google_genai import ChatGoogleGenerativeAI

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

def should_continue(state: AgentState) -> Literal["tool_node", END]:
    """Determine if the agent should continue or end."""
    messages = state["messages"]
    last_message = messages[-1]

    # If there are tool calls, continue to tools node
    if last_message.tool_calls:
        return "tool_node"

    # Otherwise, end
    return END

def tool_node(state: dict):
    """Performs the tool call"""

    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}

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
    # llm = ChatOpenAI(model="gpt-4o", temperature=0)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
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
    workflow.add_node("tool_node", tool_node)

    # Set the entry point
    workflow.set_entry_point("agent")

    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        ["tool_node", END]
    )

    # Add edge from tools back to agent
    workflow.add_edge("tool_node", "agent")

    # Compile with memory
    # memory = MemorySaver()
    app = workflow.compile()

    return app



