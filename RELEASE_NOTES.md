# Release Notes — AI Software Co-Agent v0.1.0

**Release Date:** November 6, 2026  
**Build Target:** Python 3.14.7  
**Status:** RELEASE CANDIDATE (Gate G11 Approved)

---

## 1. Executive Summary

We are pleased to announce the **v0.1.0** production release candidate of the **AI Software Co-Agent**, a deterministic, safety-guarded autonomous software engineering co-agent. Built strictly against locked specifications (Docs 01–11) and the Architecture Decision Matrix (ADM-001 to ADM-035), the system provides an end-to-end engineering loop spanning discovery, planning, controlled execution, validation, failure recovery, and multi-client interaction.

---

## 2. Key Features & Capabilities

### Controlled Engineering Lifecycle
- **Strict Monotonic State Machine**: `DISCOVERY` → `PLANNING` → `APPROVAL` → `EXECUTION` → `VALIDATION` → `COMPLETION`.
- **Atomic Modification Engine (`PatchEngine`)**: Multi-file patches are applied atomically with pre-flight base SHA-256 conflict detection and rollback.
- **Authoritative Completion Gates (`CompletionGate`)**: Tasks cannot complete without evidence-backed validation (test runs, type checks, lint checks).

### Multi-Layer Security Architecture
- **Single Tool Gateway (`ToolGateway`)**: All side effects route through unified policy authorization.
- **Workspace Isolation & Path Containment**: Hard containment blocks directory traversal and path manipulation vectors.
- **Shell Chaining & Command Injection Prevention**: Strict tokenization blocks command separators, chaining, and interpreter switches.
- **Model Context Protocol (`McpAdapter`)**: External MCP servers are isolated as untrusted capabilities with audit tracking.
- **Protected Paths**: Critical repository files (`.git/`, `.env`, keys, credentials) are permanently read/write protected.

### Client Interfaces
- **Rich Terminal CLI (`coagent`)**: Subcommands `plan`, `run`, `status`, `diff`, `cancel`, `approve`, `config`, and `health`.
- **VS Code Extension**: Interactive Chat webview, Diff review panel, Approval manager, Diagnostics provider, and Status bar indicators.

---

## 3. Quality & Verification Metrics

| Verification Check | Result | Metrics |
|---|---|---|
| **Automated Test Suite** | **PASS** | 980 tests (973 passed, 7 environment-skipped symlink tests, 0 failed) |
| **Static Type Checking** | **PASS** | `mypy` strict mode — 0 issues across 91 source files |
| **Linting & Code Style** | **PASS** | `ruff` check — 100% compliant across repository |
| **Security & Secret Scan** | **PASS** | 276 files scanned — zero secrets, tokens, or private keys detected |
| **Dependency & License Audit** | **PASS** | All release dependencies verified against permissive open-source licenses |
| **Build Reproducibility** | **PASS** | 100% bit-for-bit reproducible wheel and sdist generation |

---

## 4. Release Distribution Artifacts

| Artifact | Type | Description |
|---|---|---|
| `ai_software_co_agent-0.1.0-py3-none-any.whl` | Python Wheel | Pre-built universal binary distribution wheel |
| `ai_software_co_agent-0.1.0.tar.gz` | Source Distribution | Standard source tarball |
| `vscode/ai-software-co-agent-vscode-0.1.0.zip` | VS Code Bundle | VS Code extension source package |
| `SHA256SUMS.txt` | Checksums | Cryptographic SHA-256 digests for all release files |
| `build_manifest.json` | Build Manifest | Machine-readable build provenance and release metadata |

---

## 5. Upgrade & Installation

```bash
uv pip install dist/ai_software_co_agent-0.1.0-py3-none-any.whl
coagent --help
coagent health
```

