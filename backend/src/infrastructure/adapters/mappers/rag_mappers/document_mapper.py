from backend.src.domain.entities.rag_entities.document import (Document,
                                                               DocumentChunk)
from backend.src.infrastructure.persistence.models.rag_models import \
    DocumentModel


class DocumentMapper:
    """Handles conversion between Document entity and DocumentModel."""

    @staticmethod
    def to_model(entity: Document) -> DocumentModel:
        """Convert Document entity to DocumentModel."""
        return DocumentModel(
            id=entity.id,
            title=entity.title,
            content=entity.content,
            hash=entity.hash,
            user_id=entity.user_id

        )

    @staticmethod
    def to_entity(model: DocumentModel) -> Document:
        """Convert DocumentModel to Document entity."""
        return Document(
            id=model.id,
            title=model.title,
            content=model.content,
            hash=model.hash,
            user_id=model.user_id
        )