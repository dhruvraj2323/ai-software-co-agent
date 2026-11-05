"""Benchmark and performance baseline for repository intelligence (T055)."""

from __future__ import annotations

import time
from pathlib import Path
from uuid import uuid4

from coagent.repository.discovery import RepositoryDiscoveryService
from coagent.repository.index import RepositoryIndex
from coagent.repository.map import RepositoryMapService
from coagent.repository.search import RepositorySearchAdapter
from coagent.workspace.scope import WorkspaceScope


def test_repository_intelligence_benchmark(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "benchmark_repo"
    workspace_dir.mkdir()

    # Generate a representative multi-module structure
    packages = ["core", "services", "models", "api", "utils"]
    file_count = 0

    for pkg in packages:
        pkg_dir = workspace_dir / "src" / pkg
        pkg_dir.mkdir(parents=True)
        (pkg_dir / "__init__.py").write_text(f'"""Package {pkg}."""\n', encoding="utf-8")
        file_count += 1

        for i in range(5):
            code = f"""\"\"\"Module {pkg}_{i} description.\"\"\"

class {pkg.capitalize()}Handler{i}:
    \"\"\"Handler class {i} in {pkg}.\"\"\"
    def __init__(self, name: str):
        self.name = name

    def execute_{i}(self, data: dict):
        \"\"\"Process request in handler {i}.\"\"\"
        return data

def process_{pkg}_{i}(item_id: str) -> bool:
    \"\"\"Helper processing function.\"\"\"
    return True
"""
            (pkg_dir / f"module_{i}.py").write_text(code, encoding="utf-8")
            file_count += 1

    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    # 1. Discovery benchmark
    start_t = time.perf_counter()
    discovery = RepositoryDiscoveryService()
    files = discovery.list_files(scope)
    discovery_duration = time.perf_counter() - start_t

    assert len(files) == file_count
    assert discovery_duration < 1.0  # Fast file listing

    # 2. Indexing benchmark
    index = RepositoryIndex(discovery_service=discovery)
    start_t = time.perf_counter()
    indexed_count = index.index_workspace(scope)
    index_duration = time.perf_counter() - start_t

    assert indexed_count == file_count
    assert index_duration < 3.0  # Safe bounded indexing time

    # 3. Symbol query benchmark
    start_t = time.perf_counter()
    handlers = index.find_symbols("Handler")
    query_duration = time.perf_counter() - start_t

    from coagent.repository.symbols import SymbolKind

    classes = [s for s in handlers if s.kind == SymbolKind.CLASS]
    assert len(classes) == 25  # 5 classes * 5 packages
    assert len(handlers) == 75  # 25 classes + 50 methods
    assert query_duration < 0.2

    # 4. Search benchmark
    searcher = RepositorySearchAdapter(discovery_service=discovery)
    start_t = time.perf_counter()
    res = searcher.search_content(scope, "Helper processing function")
    search_duration = time.perf_counter() - start_t

    assert res.total_matches == 25
    assert search_duration < 0.5

    # 5. Map generation benchmark
    map_service = RepositoryMapService(discovery_service=discovery, index=index)
    start_t = time.perf_counter()
    repo_map = map_service.generate_map(scope, max_tokens=1500)
    map_duration = time.perf_counter() - start_t

    assert repo_map.file_count == file_count
    assert repo_map.token_estimate <= 1500
    assert map_duration < 0.5

    index.close()
