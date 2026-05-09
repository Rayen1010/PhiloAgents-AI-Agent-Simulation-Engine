"""
RAG package initialization.

Exports the main public components of the RAG layer:
- Embedding models/services
- Document retrievers
- Text splitters
"""

# Embeddings
from rag.embeddings import *

# Retrievers
from rag.retrievers import *

# Splitters
from rag.splitters import *

# Optional explicit public API
__all__ = [
    # Add exported classes/functions here manually if needed
]