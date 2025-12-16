import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

try:
    print("Importing tools...")
    from app.agents.rag_agent.tools import tools
    print("Tools imported successfully.")

    print("Importing prompts...")
    from app.agents.rag_agent.prompts import SYSTEM_PROMPT
    print("Prompts imported successfully.")
    
    print("Importing graph...")
    from app.agents.rag_agent.graph import create_dental_appointment_agent
    print("Graph imported successfully.")

    print("Verification Passed!")
except Exception as e:
    print(f"Verification Failed: {e}")
    sys.exit(1)
