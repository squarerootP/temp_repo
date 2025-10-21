from typing import Any, Dict, List
from cerebras.cloud.sdk import Cerebras
from langchain_core.documents import Document

from rag.config_optimized import Config
from backend.src.infrastructure.config.settings import api_settings


LLM_MODEL = api_settings.LLM_MODEL

SYSTEM_PROMPT = """You are an AI assistant that acts as a meticulous analyst for a **single document**.
You will be given snippets from this document, labeled [Source X], and your task is to answer questions
based **only** on the information contained within them.

## Core Directives
1.  **Source Integration:** Treat all provided sources ([Source 1], [Source 2], etc.) as parts of the same document.
2.  **General Queries:** If the user asks broadly (e.g., “What is this document about?”), synthesize a unified summary.
3.  **Strict Grounding:** Only use provided context. Never infer or hallucinate.
4.  **Missing Info:** If information is insufficient, say:
    “The provided document does not contain enough information to answer this question.”
5.  **Trust the Context:** Prefer source information over external knowledge.
6.  **Citations:** Every statement must cite its [Source X].
"""

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------

def format_context(docs: List[Document]) -> str:
    """Format retrieved documents into a structured context block."""
    formatted_blocks = []
    for i, doc in enumerate(docs, 1):
        source_info = doc.metadata.get("source_file", "Unknown")
        page = doc.metadata.get("page", "N/A")
        formatted_blocks.append(
            f"[Source {i} - {source_info}, Page {page}]:\n{doc.page_content.strip()}\n"
        )
    return "\n".join(formatted_blocks)


def create_prompt(question: str, context: str) -> str:
    """Build final user prompt for the model."""
    return f"""Use the following context to answer the question.
If the context does not contain enough information, clearly say so.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""


# ----------------------------------------------------------------------
# Main generation adapter
# ----------------------------------------------------------------------

def generate_response(question: str, retriever, temperature: float = None) -> Dict[str, Any]:  # type: ignore
    """Generate grounded response using retrieval-augmented generation."""
    try:
        # Retrieve relevant documents
        docs = retriever.invoke(question)
        if not docs:
            return {
                "answer": (
                    "I couldn't find relevant information in the loaded documents "
                    "to answer your question."
                ),
                "context": [],
                "sources": [],
                "model": LLM_MODEL
            }

        # Prepare prompt
        context = format_context(docs)
        prompt = create_prompt(question, context)

        # Query the LLM
        response = Cerebras.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature or Config.LLM_TEMPERATURE,
            max_tokens=Config.LLM_MAX_TOKENS
        )

        answer = response.choices[0].message.content.strip()  # type: ignore

        # Prepare formatted sources
        sources = [
            {
                "source_id": i + 1,
                "content": (
                    doc.page_content[:300] + "..."
                    if len(doc.page_content) > 300 else doc.page_content
                ),
                "metadata": {
                    "source_file": doc.metadata.get("source_file", "Unknown"),
                    "page": doc.metadata.get("page", "N/A"),
                    "chunk_index": doc.metadata.get("chunk_index", "N/A")
                }
            }
            for i, doc in enumerate(docs)
        ]

        return {
            "answer": answer,
            "context": docs,
            "sources": sources,
            "model": LLM_MODEL
        }

    except Exception as e:
        raise RuntimeError(f"LLM generation failed: {str(e)}") from e
