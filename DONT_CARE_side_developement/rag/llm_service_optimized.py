from typing import Any, Dict, List

from cerebras.cloud.sdk import Cerebras
from langchain_core.documents import Document

from rag.config_optimized import Config

SYSTEM_PROMPT = """You are an AI assistant that acts as a meticulous analyst for a **single document**. You will be given snippets from this document, labeled [Source X], and your task is to answer questions based **only** on the information contained within them.

## Core Directives
1.  **Source Integration:** The provided sources ([Source 1], [Source 2], etc.) are all parts of the **same single document**. You MUST synthesize information across all sources to form a comprehensive and unified answer.

2.  **Handling General Queries:** **If the user asks a broad question about the document as a whole** (e.g., "What is this document about?", "Summarize this document"), your task is to synthesize a high-level summary based on the main topics and themes you can identify across all provided snippets. **Start your response with "Based on the provided snippets, this document appears to be about..."**

3.  **Strict Grounding:** For all other specific questions, base your answers **exclusively** on the information within the provided context. Never infer, speculate, or use any external knowledge.

4.  **Handling Missing Information:** If, for a specific question, the combined information from all sources is insufficient, you MUST state: "The provided document does not contain enough information to answer this question."

5.  **Trust the Context:** If the provided information contradicts common knowledge, you MUST prioritize the information from the sources.

6.  **Mandatory Citations:** Every claim or piece of information in your response MUST be followed by its corresponding [Source X] citation.

## Examples

Example of WRONG behavior:
Context: [Source 1] "The sky is green." 
Question: "What color is the sky?"
❌ WRONG: "The sky is blue" (used external knowledge)
✅ CORRECT: "According to the document, the sky is green [Source 1]."

Example when info is missing:
Question: "What programming language is used?"
Context: (no mention of programming languages)
✅ CORRECT: "The provided document does not specify a programming language."
❌ WRONG: "Python is commonly used..." (hallucination)
"""

class LLMService:
    def __init__(self):
        if not Config.CEREBRAS_API_KEY:
            raise ValueError("CEREBRAS_API_KEY not found in environment")
        
        self.client = Cerebras(api_key=Config.CEREBRAS_API_KEY)
        self.model = Config.LLM_MODEL
        print(f"✓ LLM Service initialized with model: {self.model}")
    
    def _format_context(self, docs: List[Document]) -> str:
        """Format retrieved documents into context string"""
        formatted_context = []
        
        for i, doc in enumerate(docs, 1):
            source_info = doc.metadata.get('source_file', 'Unknown')
            page = doc.metadata.get('page', 'N/A')
            
            formatted_context.append(
                f"[Source {i} - {source_info}, Page {page}]:\n{doc.page_content}\n"
            )
        
        return "\n".join(formatted_context)
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create optimized prompt for LLM"""
        return f"""Use the following context to answer the question. If the context doesn't contain enough information, say so.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""
    
    def generate_response(self, question: str, retriever, temperature: float = None) -> Dict[str, Any]: #type: ignore
        """Generate response using RAG"""
        try:
            # Retrieve relevant documents
            docs = retriever.invoke(question)
            
            if not docs:
                return {
                    "answer": "I couldn't find relevant information in the loaded documents to answer your question.",
                    "context": [],
                    "sources": []
                }
            
            # Format context
            context = self._format_context(docs)
            
            # Create prompt
            prompt = self._create_prompt(question, context)
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature or Config.LLM_TEMPERATURE,
                max_tokens=Config.LLM_MAX_TOKENS
            )
            
            answer = response.choices[0].message.content #type: ignore
            
            # Format sources
            sources = [
                {
                    "source_id": i + 1,
                    "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                    "metadata": {
                        "source_file": doc.metadata.get('source_file', 'Unknown'),
                        "page": doc.metadata.get('page', 'N/A'),
                        "chunk_index": doc.metadata.get('chunk_index', 'N/A')
                    }
                }
                for i, doc in enumerate(docs)
            ]
            
            return {
                "answer": answer,
                "context": docs,
                "sources": sources,
                "model": self.model
            }
        
        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")
