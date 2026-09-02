# Bootstrap & Baseline Run Guide

## 1. Prerequisites

The development environment requires:

- Windows, Linux, or macOS
- Git
- Python 3.14.7
- uv
- A working terminal

The repository pins the Python version through .python-version.

Verify Git:

```bash

git --version
```

## 2. Clone the Repository

Clone the repository from GitHub:

```bash

git clone https://github.com/dhruvraj2323/ai-software-co-agent.git
cd ai-software-co-agent
```

Verify the active branch:

```bash

git branch --show-current
```

Verify the working tree:

```bash

git status
```


## 3. Set Up the Development Environment

From the repository root, synchronize the locked environment:

```bash

uv sync --locked --extra dev
```

This installs the project dependencies and development tools from uv.lock.

The command must complete successfully without modifying the lockfile.


## 4. Verify Python and Package Import

Verify that the environment uses the pinned Python version:

```bash

uv run python --version
```

The expected version is:

Python 3.14.7

Verify that the project package can be imported:

```bash

uv run python -c "import coagent; print('coagent import: PASS')"
```


## 5. Environment Variables and Secrets

The repository provides .env.example as the template for local environment configuration.

Create a local .env file when environment variables are required:

```bash

copy .env.example .env
```

The .env file is local-only and must never be committed to Git.

Do not place real API keys, passwords, access tokens, private keys, or other secrets directly in repository configuration files.

Configuration files may reference environment variables using the supported ${VARIABLE_NAME} pattern.


## 6. Run Tests

Run the project test suite:

```bash

uv run pytest -q
```

The baseline foundation test suite must complete successfully.


## 7. Run Ruff Validation

Run the Ruff linter:

```bash

uv run ruff check .
```

Run the Ruff formatter check:

```bash

uv run ruff format --check .
```

Both commands must complete successfully.


## 8. Run Mypy Validation

Run static type checking for the project source, CLI, and CI scripts:

```bash

uv run mypy src cli scripts
```

The command must complete successfully without type-checking errors.


## 9. Run the Security Scan

Run the repository security scanner:

```bash

uv run python scripts/ci/security_scan.py
```

The scanner must report:

SECURITY SCAN: PASS

The security scan must complete successfully before changes are considered ready for commit.


## 10. Complete Baseline Validation

A new developer has reproduced the foundation baseline when all of the following checks pass:

1. `uv sync --locked --extra dev`
2. `uv run python --version` reports Python 3.14.7.
3. The `coagent` package imports successfully.
4. `uv run pytest -q` passes.
5. `uv run ruff check .` passes.
6. `uv run ruff format --check .` passes.
7. `uv run mypy src cli scripts` passes.
8. `uv run python scripts/ci/security_scan.py` reports `SECURITY SCAN: PASS`.

The working tree should remain clean after validation, except for intentional local changes.
