from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from datetime import datetime, timezone, timedelta
from uuid import uuid4
# from app.config import settings
from sqlalchemy import text, inspect
import re

# ============================================
# LOAD ENV VARIABLES
# ============================================
# from langchain_community.utilities import SQLDatabase

# DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/dental_appointment_db"
# db = SQLDatabase.from_uri(settings.DATABASE_URL)
from app.database import get_db
from app.database import engine 
from app.agents.scheduler_agent.table_schemas import table_schemas

db = get_db()

# ============================================
# TOOL DEFINITIONS
# ============================================

@tool
async def get_database_schema(table_names: str = "") -> str:
    """
    Returns schema information from the predefined SQLAlchemy schema hashmap,
    instead of querying the database.
    """

    # -------------------------------------------------------------------
    # Static schema hashmap
    # -------------------------------------------------------------------
    SCHEMA = table_schemas

    # -------------------------------------------------------------------
    # If no table names provided → return list of tables
    # -------------------------------------------------------------------
    if not table_names:
        available = ", ".join(SCHEMA.keys())
        return f"Available tables: {available}"

    # -------------------------------------------------------------------
    # Process requested tables
    # -------------------------------------------------------------------
    tables = [t.strip() for t in table_names.split(",")]
    output = ""

    for table in tables:
        if table not in SCHEMA:
            output += f"\n❌ Table '{table}' does not exist.\n"
            continue

        table_info = SCHEMA[table]
        output += f"\n📌 Schema for `{table}`\n"
        output += f"Description: {table_info['description']}\n"
        output += "-" * 60 + "\n"
        
        for col in table_info['columns']:
            output += f"• {col['name']}"
            if col['is_primary_key']:
                output += " (PK)"
            if col['is_foreign_key']:
                output += " (FK)"
            output += f": {col['description']}"
            if col.get('unique_values'):
                output += f" (Unique values: {', '.join(str(v) for v in col['unique_values'])})"
            output += "\n"
        output += "\n"

    return output

@tool
def planner(question: str) -> str:
    """
    Create a step-by-step execution plan for complex, multi-part questions.
    This tool should only be used when the user's request requires multiple
    separate operations or decisions to fully address.
    
    Args:
        question: The user's question or request that needs planning
        
    Returns:
        A structured, numbered plan with clear steps to address the request
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # Build schema context from the imported table_schemas
    schema_context = ""
    for table_name, table_info in table_schemas.items():
        schema_context += f"\nTable: {table_name}\n"
        schema_context += f"Description: {table_info['description']}\n"
        for col in table_info['columns']:
             schema_context += f"- {col['name']}: {col['description']}"
             if col['use_cases']:
                 schema_context += f" (Used for: {', '.join(col['use_cases'])})"
             if col.get('unique_values'):
                 schema_context += f" (Unique values: {', '.join(str(v) for v in col['unique_values'])})"
             schema_context += "\n"
    
    prompt = f"""You are a dental appointment scheduling expert. Break down the following
    complex request into clear, sequential steps.
    
    You have access to the following database schema:
    {schema_context}
    
    Request: {question}
    
    Format your response as a numbered list of steps. Be concise but thorough.
    Each step should be:
    1. Specific and actionable
    2. Include any necessary context or data requirements
    3. Note any dependencies between steps
    4. Consider appointment booking workflows and constraints
    
    If the request is simple and doesn't require planning, say so. The steps cannot be more than 3."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()

@tool
def generate_sql_query(natural_language_question: str, schema_context: str) -> str:
    """
    Generate a SQL query from a natural language question.
    This tool uses an LLM to convert the user's question into a valid SQL query.

    Args:
        natural_language_question: The user's question in plain English
        schema_context: Relevant database schema information, MUST include sample rows

    Returns:
        A SQL query string
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    prompt = f"""You are a SQL expert for a dental appointment booking system.

                Database Schema:
                {schema_context}

                User Question: {natural_language_question}

                Important Guidelines:
                - Generate ONLY SELECT , UPDATE, INSERT queries (no DELETE, DROP, ALTER, CREATE, TRUNCATE)
                - Always use proper JOIN syntax when multiple tables are needed
                - Include relevant WHERE clauses to filter results
                - Use table aliases for readability
                - Limit results to a reasonable number (use LIMIT 10 unless user specifies)
                - For appointment times, remember they are stored in UTC
                - Return ONLY the SQL query, no explanation

                Generate the SQL query:"""

    response = llm.invoke([HumanMessage(content=prompt)])
    sql_query = response.content.strip()

    # Remove markdown code blocks if present
    if sql_query.startswith("```sql"):
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

    return sql_query


@tool
def validate_sql_query(sql_query: str) -> str:
    """
    Validate a SQL query for common mistakes and security issues.

    Args:
        sql_query: The SQL query to validate

    Returns:
        Either "VALID" or an error message with corrections needed
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    prompt = f"""You are a SQL expert reviewing this query for correctness and safety.

                SQL Query:
                {sql_query}

                Check for:
                1. Security: Ensure no DML statements (DELETE, DROP, ALTER, CREATE, TRUNCATE)
                2. Syntax: Check for SQL syntax errors
                3. Logic: Verify JOINs are correct, proper WHERE clauses
                4. Data types: Check for type mismatches
                5. Best practices: Proper use of LIMIT, correct column names

                If the query is valid, respond with only: VALID

                If there are issues, respond with: ERROR: [description of the issue]"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()


@tool
def format_query_results(query_result: str, original_question: str) -> str:
    """
    Convert SQL query results into a natural language response.

    Args:
        query_result: The raw SQL query result
        original_question: The user's original question

    Returns:
        A natural language answer to the user's question
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

    prompt = f"""You are a helpful dental office assistant. Convert the database query results 
    into a clear, natural language response.

                User's Question: {original_question}

                Query Results: {query_result}

                Provide a friendly, conversational response that:
                - Directly answers the user's question
                - Is easy to understand (no technical jargon)
                - Formats information clearly (use bullet points if helpful)
                - Adds context where appropriate (e.g., "Dr. Smith specializes in...")
                - For appointment times, mention the timezone if relevant

                Response:"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()



#---------------------------------------------
# READ & WRITE OPERATION TOOLS (Safe and Controlled)
#---------------------------------------------

@tool
async def execute_sql_query(sql_query: str) -> str:
    """
    Execute a SQL query on the PostgreSQL database using async SQLAlchemy.
    ONLY executes SELECT, UPDATE, INSERT queries for safety.

    Args:
        sql_query: The SQL query to execute.

    Returns:
        Query results as a string, or an error message.
    """


    # --------------------------------------
    # Pre-process / normalize
    # --------------------------------------
    original_query = sql_query.strip()
    query_upper = original_query.upper()

    # --------------------------------------
    # Safety checks
    # --------------------------------------
    if not (
        query_upper.startswith("SELECT")
        or query_upper.startswith("INSERT")
        or query_upper.startswith("UPDATE")
    ):
        return "ERROR: Only SELECT, INSERT, and UPDATE queries are allowed."

    # Block dangerous operations (whole-word)
    forbidden = ["DROP", "DELETE", "ALTER", "CREATE", "TRUNCATE"]
    pattern = r"\b(" + "|".join(forbidden) + r")\b"

    if re.search(pattern, query_upper):
        return "ERROR: Query contains forbidden operations."

    # --------------------------------------
    # Auto-add RETURNING * if missing
    # --------------------------------------
    if (query_upper.startswith("INSERT") or query_upper.startswith("UPDATE")) \
       and "RETURNING" not in query_upper:
        sql_query = original_query.rstrip(";") + " RETURNING *"
    else:
        sql_query = original_query

    try:
        async for session in get_db():
            stmt = text(sql_query)
            result = await session.execute(stmt)

            # --------------------------------------
            # Handle SELECT or INSERT/UPDATE that returns rows
            # --------------------------------------
            if result.returns_rows:
                rows = result.mappings().all()
                await session.commit()

                if not rows:
                    return "Query executed successfully but returned no rows."

                return str([dict(r) for r in rows])

            # --------------------------------------
            # Handle INSERT/UPDATE with no result (rare with our modification)
            # --------------------------------------
            await session.commit()
            return "Query executed successfully."

    except Exception as e:
        return f"ERROR executing query: {str(e)}"




# ============================================
# WRITE OPERATION TOOLS (Safe and Controlled)
# ============================================

@tool
def create_appointment(
    user_id: str,
    provider_id: str,
    service_id: str,
    start_time: str,
    timezone_str: str,
    chief_complaint: str = "",
    notes: str = "",
    created_by: str = "ai_agent"
) -> str:
    """
    Create a new appointment in the database.
    This tool safely executes an INSERT operation with validation.

    Args:
        user_id: UUID of the patient (from users table)
        provider_id: UUID of the dentist/hygienist (from service_providers table)
        service_id: UUID of the service (from services table)
        start_time: ISO format datetime (e.g., "2025-11-01T14:00:00")
        timezone_str: IANA timezone (e.g., "America/Chicago")
        chief_complaint: Reason for visit
        notes: Additional notes
        created_by: Who created the appointment (default: ai_agent)

    Returns:
        Success message with appointment ID or error message
    """
    try:
        # Validate UUIDs format (basic check)
        from uuid import UUID
        UUID(user_id)
        UUID(provider_id)
        UUID(service_id)

        # Parse and validate datetime
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))

        # Get service duration to calculate end_time
        duration_query = text("SELECT duration_minutes FROM services WHERE id = :service_id")
        result = db.execute(duration_query, {"service_id": service_id}).fetchone()

        if not result:
            return f"ERROR: Service with ID {service_id} not found"

        duration_minutes = result[0]
        end_dt = start_dt + timedelta(minutes=duration_minutes)

        # Generate new appointment ID
        appointment_id = str(uuid4())

        # Insert appointment using parameterized query
        insert_query = text("""
            INSERT INTO appointments (
                id, user_id, provider_id, service_id,
                start_time, end_time, timezone, status,
                chief_complaint, notes, created_by, created_at
            ) VALUES (
                :id, :user_id, :provider_id, :service_id,
                :start_time, :end_time, :timezone, :status,
                :chief_complaint, :notes, :created_by, :created_at
            )
        """)

        db.execute(insert_query, {
            "id": appointment_id,
            "user_id": user_id,
            "provider_id": provider_id,
            "service_id": service_id,
            "start_time": start_dt,
            "end_time": end_dt,
            "timezone": timezone_str,
            "status": "scheduled",
            "chief_complaint": chief_complaint,
            "notes": notes,
            "created_by": created_by,
            "created_at": datetime.now(timezone.utc)
        })

        # Commit the transaction
        db.commit()

        return f"SUCCESS: Appointment created with ID {appointment_id}. Scheduled for {start_time} ({timezone_str})"

    except ValueError as e:
        return f"ERROR: Invalid input format - {str(e)}"
    except Exception as e:
        db.rollback()
        return f"ERROR: Failed to create appointment - {str(e)}"


@tool
def update_appointment(
    appointment_id: str,
    new_start_time: str = None,
    new_provider_id: str = None,
    new_service_id: str = None,
    new_notes: str = None
) -> str:
    """
    Update (reschedule) an existing appointment.

    Args:
        appointment_id: UUID of the appointment to update
        new_start_time: New ISO format datetime (optional)
        new_provider_id: New provider UUID (optional)
        new_service_id: New service UUID (optional)
        new_notes: Updated notes (optional)

    Returns:
        Success message or error message
    """
    try:
        from uuid import UUID
        UUID(appointment_id)

        # Build dynamic update query
        update_fields = []
        params = {"appointment_id": appointment_id}

        if new_start_time:
            start_dt = datetime.fromisoformat(new_start_time.replace('Z', '+00:00'))

            # Get current service to calculate new end_time
            service_query = text("""
                SELECT s.duration_minutes 
                FROM appointments a 
                JOIN services s ON a.service_id = s.id 
                WHERE a.id = :appointment_id
            """)
            result = db.execute(service_query, {"appointment_id": appointment_id}).fetchone()

            if not result:
                return f"ERROR: Appointment {appointment_id} not found"

            duration = result[0]
            end_dt = start_dt + timedelta(minutes=duration)

            update_fields.append("start_time = :start_time")
            update_fields.append("end_time = :end_time")
            params["start_time"] = start_dt
            params["end_time"] = end_dt

        if new_provider_id:
            UUID(new_provider_id)
            update_fields.append("provider_id = :provider_id")
            params["provider_id"] = new_provider_id

        if new_service_id:
            UUID(new_service_id)
            update_fields.append("service_id = :service_id")
            params["service_id"] = new_service_id

        if new_notes:
            update_fields.append("notes = :notes")
            params["notes"] = new_notes

        if not update_fields:
            return "ERROR: No fields provided to update"

        # Add updated_at timestamp
        update_fields.append("updated_at = :updated_at")
        params["updated_at"] = datetime.now(timezone.utc)

        # Execute update
        update_query = text(f"""
            UPDATE appointments 
            SET {', '.join(update_fields)}
            WHERE id = :appointment_id
        """)

        result = db.execute(update_query, params)
        db.commit()

        if result.rowcount == 0:
            return f"ERROR: Appointment {appointment_id} not found"

        return f"SUCCESS: Appointment {appointment_id} updated successfully"

    except ValueError as e:
        return f"ERROR: Invalid input format - {str(e)}"
    except Exception as e:
        db.rollback()
        return f"ERROR: Failed to update appointment - {str(e)}"


@tool
def cancel_appointment(
    appointment_id: str,
    cancellation_reason: str = "",
    cancelled_by: str = "patient"
) -> str:
    """
    Cancel an existing appointment by updating its status.

    Args:
        appointment_id: UUID of the appointment to cancel
        cancellation_reason: Reason for cancellation
        cancelled_by: Who cancelled (patient, staff, provider)

    Returns:
        Success message or error message
    """
    try:
        from uuid import UUID
        UUID(appointment_id)

        # Update appointment status to cancelled
        cancel_query = text("""
            UPDATE appointments 
            SET 
                status = 'cancelled',
                cancellation_reason = :reason,
                cancelled_by = :cancelled_by,
                cancelled_at = :cancelled_at,
                updated_at = :updated_at
            WHERE id = :appointment_id
            AND status != 'cancelled'
        """)

        result = db.execute(cancel_query, {
            "appointment_id": appointment_id,
            "reason": cancellation_reason,
            "cancelled_by": cancelled_by,
            "cancelled_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        })

        db.commit()

        if result.rowcount == 0:
            return f"ERROR: Appointment {appointment_id} not found or already cancelled"

        return f"SUCCESS: Appointment {appointment_id} has been cancelled"

    except ValueError as e:
        return f"ERROR: Invalid appointment ID format - {str(e)}"
    except Exception as e:
        db.rollback()
        return f"ERROR: Failed to cancel appointment - {str(e)}"


@tool
def confirm_appointment(appointment_id: str) -> str:
    """
    Confirm a scheduled appointment by updating its status.

    Args:
        appointment_id: UUID of the appointment to confirm

    Returns:
        Success message or error message
    """
    try:
        from uuid import UUID
        UUID(appointment_id)

        confirm_query = text("""
            UPDATE appointments 
            SET 
                status = 'confirmed',
                confirmed_at = :confirmed_at,
                updated_at = :updated_at
            WHERE id = :appointment_id
            AND status = 'scheduled'
        """)

        result = db.execute(confirm_query, {
            "appointment_id": appointment_id,
            "confirmed_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        })

        db.commit()

        if result.rowcount == 0:
            return f"ERROR: Appointment {appointment_id} not found or not in scheduled status"

        return f"SUCCESS: Appointment {appointment_id} has been confirmed"

    except ValueError as e:
        return f"ERROR: Invalid appointment ID format - {str(e)}"
    except Exception as e:
        db.rollback()
        return f"ERROR: Failed to confirm appointment - {str(e)}"

tools = [
    get_database_schema,
    planner,
    generate_sql_query,
    validate_sql_query,
    execute_sql_query,
    format_query_results,
    create_appointment,
    update_appointment,
    cancel_appointment,
    confirm_appointment
]