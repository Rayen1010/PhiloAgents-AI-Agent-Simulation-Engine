"""Custom exceptions for chatbot domain"""


class ChatbotException(Exception):
    """Base exception for chatbot domain"""
    pass


class ChatbotNotFound(ChatbotException):
    """Raised when chatbot configuration is not found"""
    pass


class ConversationError(ChatbotException):
    """Raised when conversation processing fails"""
    pass


class RAGError(ChatbotException):
    """Raised when RAG pipeline fails"""
    pass


class EvaluationError(ChatbotException):
    """Raised when evaluation fails"""
    pass
