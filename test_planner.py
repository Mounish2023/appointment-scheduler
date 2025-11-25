import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.agents.scheduler_agent.tools import planner

def test_planner():
    print("Testing planner tool...")
    question = "I need to book an appointment for a root canal next Tuesday with a dentist who has at least 5 years of experience."
    
    try:
        plan = planner.invoke(question)
        print("\nGenerated Plan:")
        print(plan)
        print("\nTest Passed!")
    except Exception as e:
        print(f"\nTest Failed: {e}")

if __name__ == "__main__":
    test_planner()
