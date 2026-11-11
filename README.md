# pydedup

Find duplicate Python source blocks within or across files.

## About

`pydedup` scans Python project trees for duplicate code blocks, optionally within a single file or across multiple files. It produces a compact report and a JSON artifact for review.

## Features

- Duplicate block detection using normalized slice hashing
- Configurable minimum block length
- Reports duplicates within the same file and across files
- Excludes common non-source directories: `.git`, `__pycache__`, `.venv`, `dist`, `build`, `node_modules`
- JSON and human-readable output

## Installation

```bash
python -m pip install -e .
```

## Usage

```bash
# Scan the current directory
python -m pydedup.cli .

# Require at least 10 lines
python -m pydedup.cli . --min-lines 10

# JSON output
python -m pydedup.cli . --json /tmp/pydedup.json
```

## Project structure

```
.gitignore
LICENSE
README.md
pyproject.toml
.github/
  workflows/
    ci.yml
pydedup/
  __init__.py
  cli.py
  scan.py
tests/
  test_pydedup.py
```

## Tags / keywords

duplicate-detection, python, static-analysis, code-quality, developer-tools, duplicate-code

Source: https://github.com/felixhartmannnn/pydedup
