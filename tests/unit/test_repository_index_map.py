"""Unit tests for repository index and map service."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from coagent.repository.index import RepositoryIndex
from coagent.repository.map import RepositoryMapService
from coagent.workspace.scope import WorkspaceScope


def test_repository_index_and_invalidation(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()

    app_py = workspace_dir / "app.py"
    app_py.write_text("class Application:\n    def run(self):\n        pass\n", encoding="utf-8")

    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    index = RepositoryIndex()
    indexed_count = index.index_workspace(scope)
    assert indexed_count == 1

    file_rec = index.get_file("app.py")
    assert file_rec is not None
    assert file_rec.relative_path == "app.py"
    assert index.is_fresh(scope, "app.py") is True

    syms = index.get_symbols_for_file("app.py")
    assert len(syms) == 2  # Application, Application.run

    # Search symbols
    found = index.find_symbols("App")
    assert len(found) >= 1
    assert found[0].name == "Application"

    # Modify file
    app_py.write_text("class Application:\n    def start(self):\n        pass\n", encoding="utf-8")
    assert index.is_fresh(scope, "app.py") is False

    # Invalidate
    index.invalidate("app.py")
    assert index.get_file("app.py") is None
    assert len(index.get_symbols_for_file("app.py")) == 0

    index.close()


def test_repository_map_service(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()

    src_dir = workspace_dir / "src"
    src_dir.mkdir()
    (src_dir / "main.py").write_text("class Server:\n    pass\n", encoding="utf-8")
    (workspace_dir / "README.md").write_text("# Docs", encoding="utf-8")

    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    index = RepositoryIndex()
    index.index_workspace(scope)

    map_service = RepositoryMapService(index=index)
    repo_map = map_service.generate_map(scope, max_tokens=500)

    assert repo_map.file_count == 2
    assert "README.md" in repo_map.content
    assert "main.py" in repo_map.content
    assert "classes: Server" in repo_map.content
    assert repo_map.token_estimate > 0

    index.close()

