"""Deprecated shim.

This module used to provide a separate graph-only RAG implementation. The
implementation has been consolidated into `_rag_repository_impl.py`. To keep
backwards compatibility for imports, re-export the canonical implementation
from there. New code should import `LangGraphRAGRepositoryImpl` directly from
`_rag_repository_impl`.
"""

from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.rag_repository_impl import \
    LangGraphRAGRepositoryImpl

# Keep both names available for backwards compatibility
LangGraphRAGRepository = LangGraphRAGRepositoryImpl

__all__ = ["LangGraphRAGRepository", "LangGraphRAGRepositoryImpl"]
