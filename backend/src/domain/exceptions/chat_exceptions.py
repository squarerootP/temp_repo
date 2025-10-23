class ChatHistoryNotFound(Exception):
    """Exception raised when a chat history is not found."""
    pass
class ChatSessionAlreadyExists(Exception):
    """Exception raised when trying to create a chat session that already exists."""
    pass
class FileSizeExceeded(Exception):
    """Exception raised when the uploaded file size exceeds the allowed limit."""
    pass
class UnsupportedFileType(Exception):
    """Exception raised when the uploaded file type is not supported."""
    pass

class ChatSessionNotFoundError(Exception):
    """Exception raised when a chat session is not found."""
    pass

class MessageProcessingError(Exception):
    """Exception raised when there is an error processing a chat message."""
    pass
class SessionCreationError(Exception):
    """Exception raised when there is an error creating a chat session."""
    pass