"""Unit tests for symbol intelligence extractor."""

from __future__ import annotations

from pathlib import Path

from coagent.repository.symbols import PythonSymbolExtractor, SymbolKind, SymbolRegistry


def test_python_symbol_extractor(tmp_path: Path) -> None:
    code = '''
"""Module docstring."""

class UserRepository:
    """Manages users."""
    def __init__(self, db):
        self.db = db

    async def get_user_by_id(self, user_id: str):
        """Fetch a user."""
        return None

def standalone_function(x, y):
    """Adds two numbers."""
    return x + y
'''
    py_file = tmp_path / "repo.py"
    py_file.write_text(code, encoding="utf-8")

    extractor = PythonSymbolExtractor()
    assert extractor.can_handle(py_file) is True

    symbols = extractor.extract_symbols(py_file)
    assert len(symbols) == 4

    names = {s.name: s for s in symbols}

    assert "UserRepository" in names
    cls_sym = names["UserRepository"]
    assert cls_sym.kind == SymbolKind.CLASS
    assert cls_sym.docstring == "Manages users."

    assert "UserRepository.__init__" in names
    init_sym = names["UserRepository.__init__"]
    assert init_sym.kind == SymbolKind.METHOD
    assert init_sym.parent_symbol == "UserRepository"

    assert "UserRepository.get_user_by_id" in names
    async_sym = names["UserRepository.get_user_by_id"]
    assert async_sym.kind == SymbolKind.METHOD
    assert "async def get_user_by_id" in (async_sym.signature or "")

    assert "standalone_function" in names
    func_sym = names["standalone_function"]
    assert func_sym.kind == SymbolKind.FUNCTION
    assert func_sym.docstring == "Adds two numbers."


def test_symbol_registry(tmp_path: Path) -> None:
    py_file = tmp_path / "test.py"
    py_file.write_text("def ping(): pass\n", encoding="utf-8")

    txt_file = tmp_path / "test.txt"
    txt_file.write_text("plain text", encoding="utf-8")

    registry = SymbolRegistry()
    assert len(registry.extract_symbols(py_file)) == 1
    assert len(registry.extract_symbols(txt_file)) == 0

