"""Symbol intelligence interface and language extractors."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol


class SymbolKind(StrEnum):
    """Classification of extracted code symbols."""

    CLASS = "CLASS"
    FUNCTION = "FUNCTION"
    METHOD = "METHOD"
    VARIABLE = "VARIABLE"
    IMPORT = "IMPORT"
    INTERFACE = "INTERFACE"


@dataclass(frozen=True)
class SymbolInfo:
    """Structured representation of a source code symbol."""

    name: str
    kind: SymbolKind
    file_path: str
    line_start: int
    line_end: int
    signature: str | None = None
    docstring: str | None = None
    parent_symbol: str | None = None


class SymbolProvider(Protocol):
    """Protocol for language-specific symbol extraction."""

    def can_handle(self, file_path: Path) -> bool:
        """Return True if this provider can extract symbols for the given file."""
        ...

    def extract_symbols(self, file_path: Path, content: str | None = None) -> list[SymbolInfo]:
        """Extract structured symbols from file contents."""
        ...


class PythonSymbolExtractor:
    """AST-based symbol extractor for Python files."""

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in {".py", ".pyi"}

    def extract_symbols(self, file_path: Path, content: str | None = None) -> list[SymbolInfo]:
        """Extract classes, functions, and methods from Python source."""
        if content is None:
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                return []

        try:
            tree = ast.parse(content, filename=str(file_path))
        except (SyntaxError, ValueError):
            return []

        rel_path = str(file_path).replace("\\", "/")
        symbols: list[SymbolInfo] = []

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                symbols.extend(self._process_class(node, rel_path))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                symbols.append(self._process_function(node, rel_path, parent=None))

        return symbols

    def _process_class(self, node: ast.ClassDef, file_path: str) -> list[SymbolInfo]:
        results: list[SymbolInfo] = []
        bases = [ast.unparse(b) for b in node.bases]
        sig = f"class {node.name}({', '.join(bases)})" if bases else f"class {node.name}"
        doc = ast.get_docstring(node)

        results.append(
            SymbolInfo(
                name=node.name,
                kind=SymbolKind.CLASS,
                file_path=file_path,
                line_start=node.lineno,
                line_end=node.end_lineno or node.lineno,
                signature=sig,
                docstring=doc[:200] if doc else None,
                parent_symbol=None,
            )
        )

        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                results.append(self._process_function(child, file_path, parent=node.name))

        return results

    def _process_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: str,
        parent: str | None = None,
    ) -> SymbolInfo:
        doc = ast.get_docstring(node)
        is_async = isinstance(node, ast.AsyncFunctionDef)
        prefix = "async def " if is_async else "def "

        arg_names = [arg.arg for arg in node.args.args]
        sig = f"{prefix}{node.name}({', '.join(arg_names)})"

        kind = SymbolKind.METHOD if parent else SymbolKind.FUNCTION

        return SymbolInfo(
            name=f"{parent}.{node.name}" if parent else node.name,
            kind=kind,
            file_path=file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            signature=sig,
            docstring=doc[:200] if doc else None,
            parent_symbol=parent,
        )


class SymbolRegistry:
    """Registry managing language-specific symbol extractors."""

    def __init__(self, extractors: list[SymbolProvider] | None = None) -> None:
        self._extractors: list[SymbolProvider] = extractors or [PythonSymbolExtractor()]

    def extract_symbols(self, file_path: Path, content: str | None = None) -> list[SymbolInfo]:
        for extractor in self._extractors:
            if extractor.can_handle(file_path):
                return extractor.extract_symbols(file_path, content=content)
        return []

