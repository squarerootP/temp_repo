from backend.src.domain.entities.rag_entities.document import Document
from backend.src.infrastructure.persistence.models.rag_models import \
    DocumentModel


class DocumentMapper:
    """Handles conversion between Document entity and DocumentModel."""

    @staticmethod
    def to_model(entity: Document) -> DocumentModel:
        """Convert Document entity to DocumentModel."""
        return DocumentModel(
            book_isbn=entity.book_isbn,
            title=entity.title,
            content=entity.content,
            hash=entity.hash,
        )

    @staticmethod
    def to_entity(model: DocumentModel) -> Document:
        """Convert DocumentModel to Document entity."""
        return Document(
            book_isbn=model.book_isbn,
            title=model.title,
            content=model.content,
            hash=model.hash,
        )
