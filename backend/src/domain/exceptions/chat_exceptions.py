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
