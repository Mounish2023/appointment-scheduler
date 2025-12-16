from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from app.services.search_client import AzureSearchService
from app.config import settings
from azure.search.documents.models import VectorFilterMode, VectorizedQuery
from typing import Optional, List, Union
from app.services.cohere_client import CohereClient

@tool
def search_knowledge_base(query: str) -> str:
    """
    Search Azure AI Search index for relevant documents with a query.
    This tool should be used to retrieve context for answering user questions.
    """
    try:
        service = AzureSearchService()
        client = service.get_client()
        cohere_client = CohereClient()

        search_query_vector = cohere_client.generate_query_vector(query)
        vector_query = VectorizedQuery(
             vector=search_query_vector,
             k_nearest_neighbors=5,
             fields="chunk_embedding",
             kind="vector",
             exhaustive=True
         )

        
        # Search for the top 5 most relevant documents
        results = client.search(search_text=query, top=5, vector_queries=[vector_query])

        formatted_results = []
        for result in results:
            # Using the provided schema for formatting the document chunks
            doc_id = result.get("document_id", "N/A")
            chunk_id = result.get("chunk_id", "N/A")
            document_title = result.get("document_title", "N/A")
            chunk_content = result.get("chunk_raw_content", "No content available.")
            page_number = result.get("chunk_page_number", "N/A")

            formatted_results.append(
                f"Document ID: {doc_id}\n"
                f"Chunk ID: {chunk_id}\n"
                f"Document Title: {document_title}\n"
                f"Content: {chunk_content}\n"
                f"Page Number: {page_number}\n"
            )

        if not formatted_results:
            return "No relevant documents found."

        return "\n---\n".join(formatted_results)
    except Exception as e:
        return f"Error searching Azure AI Search: {str(e)}"

@tool
def generate_answer(query: str, relevant_documents: str, feedback: str = "") -> str:
    """
    Generate an answer from query, relevant documents and optional feedback.
    If relevant documents are not found or insufficient, say so.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)

    prompt = f"""You are a helpful assistant. Answer the user's query using ONLY the provided Relevant Documents.

CRITICAL RULES:
- You MUST include citations for every factual claim.
- Use ONLY the information in Relevant Documents. Do NOT use outside knowledge.
- If the Relevant Documents do not contain enough information to answer, say so explicitly.
- Do NOT cite anything that is not in Relevant Documents.

CITATION FORMAT (ONLY document_id + page_number):
- Add citations in square brackets.
- Use this exact format: [doc:<document_id>|p:<page_number>]
  Examples:
  - [doc:1|p:2]
  - [doc:PolicyA|p:5]
- If multiple documents/pages support a claim, include multiple citations:
  [doc:1|p:2][doc:2|p:1]

INPUTS:
Query: {query}

Relevant Documents:
{relevant_documents}
"""

    if feedback:
        prompt += f"""
Previous Answer Feedback:
{feedback}

Revise the answer to address the feedback while still following ALL citation rules above.
"""

    prompt += "\nAnswer (with citations):"

    response = llm.invoke(prompt)
    return response.content

@tool
def evaluate_answer(query: str, answer: str, relevant_documents: str) -> str:
    """
    Evaluate the answer accuracy against the relevant documents.
    Returns 'ACCURATE' if the answer is supported by documents, or feedback on what is wrong.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)

    prompt = f"""You are a strict evaluator.

Task:
Evaluate whether the provided ANSWER is accurate and FULLY supported by the RELEVANT DOCUMENTS for the given QUERY.

Hard rules:
- Treat the documents as the ONLY source of truth. Do NOT use outside knowledge.
- Check BOTH content and citations in the answer.
- The answer must use citations in this exact format: [doc:<document_id>|p:<page_number>]
- Every factual claim must have at least one citation immediately after it (or at minimum within the same bullet/sentence).
- Citations must reference documents/pages that actually support the claim.
- If a claim is not supported OR is missing a citation OR has an incorrect citation, it is NOT accurate.

Inputs:
Query: {query}

Relevant Documents:
{relevant_documents}

Answer:
{answer}

Your output format:
- If the answer is fully supported AND citations are correctly used, output exactly:
ACCURATE

- Otherwise, output feedback ONLY (do not output "ACCURATE") using this structure:

VERDICT: INACCURATE
ISSUES:
1) <issue description>
2) <issue description>
...
FIX INSTRUCTIONS:
- <actionable fix>
- <actionable fix>
...

While listing issues, explicitly quote the problematic claim(s) from the ANSWER and say whether it is:
- UNSUPPORTED (not in documents)
- HALLUCINATED (contradicts documents or invents details)
- CITATION_MISSING (no citation)
- CITATION_WRONG (citation doesn't support claim)
- OVERSTATED (documents weaker than claim)
"""

    response = llm.invoke(prompt)
    return response.content

tools = [search_knowledge_base, generate_answer, evaluate_answer]
tools_by_name = {tool.name: tool for tool in tools}



