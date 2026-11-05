"""Repository intelligence package providing discovery, search, symbols, and indexing."""

from coagent.repository.discovery import (
    DEFAULT_IGNORED_DIRS,
    DEFAULT_IGNORED_PATTERNS,
    RepositoryDiscoveryService,
    RepositoryInfo,
)
from coagent.repository.index import IndexedFile, RepositoryIndex
from coagent.repository.map import RepositoryMap, RepositoryMapService
from coagent.repository.search import (
    RepositorySearchAdapter,
    SearchMatch,
    SearchResult,
)
from coagent.repository.symbols import (
    PythonSymbolExtractor,
    SymbolInfo,
    SymbolKind,
    SymbolProvider,
    SymbolRegistry,
)

__all__ = [
    "DEFAULT_IGNORED_DIRS",
    "DEFAULT_IGNORED_PATTERNS",
    "IndexedFile",
    "PythonSymbolExtractor",
    "RepositoryDiscoveryService",
    "RepositoryIndex",
    "RepositoryInfo",
    "RepositoryMap",
    "RepositoryMapService",
    "RepositorySearchAdapter",
    "SearchMatch",
    "SearchResult",
    "SymbolInfo",
    "SymbolKind",
    "SymbolProvider",
    "SymbolRegistry",
]
