"""Lint tests for Power of 10 rules that Ruff and mypy can't check.

Rule 1: no recursion.  Rule 2: every loop has a fixed bound.  Rule 4: short functions.
"""

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = sorted([*(ROOT / "src").rglob("*.py"), *(ROOT / "tests").rglob("*.py")])
MAX_FUNCTION_LINES = 60

FunctionNode = ast.FunctionDef | ast.AsyncFunctionDef


def _functions(path: Path) -> list[FunctionNode]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return [n for n in ast.walk(tree) if isinstance(n, FunctionNode)]


def _label(path: Path, node: ast.AST) -> str:
    return f"{path.relative_to(ROOT)}:{getattr(node, 'lineno', '?')}"


def _calls_itself(func: FunctionNode) -> bool:
    return any(
        isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == func.name
        for node in ast.walk(func)
    )


def _is_constant_true(test: ast.expr) -> bool:
    return isinstance(test, ast.Constant) and bool(test.value)


def test_source_files_found() -> None:
    assert len(SOURCE_FILES) >= 3


@pytest.mark.parametrize("path", SOURCE_FILES, ids=lambda p: p.name)
def test_functions_fit_on_one_page(path: Path) -> None:
    too_long = [
        f"{_label(path, f)} {f.name}() is {(f.end_lineno or f.lineno) - f.lineno + 1} lines"
        for f in _functions(path)
        if (f.end_lineno or f.lineno) - f.lineno + 1 > MAX_FUNCTION_LINES
    ]
    assert not too_long, f"Functions over {MAX_FUNCTION_LINES} lines: {too_long}"


@pytest.mark.parametrize("path", SOURCE_FILES, ids=lambda p: p.name)
def test_no_direct_recursion(path: Path) -> None:
    recursive = [f"{_label(path, f)} {f.name}()" for f in _functions(path) if _calls_itself(f)]
    assert not recursive, f"Recursive functions: {recursive}"


@pytest.mark.parametrize("path", SOURCE_FILES, ids=lambda p: p.name)
def test_no_unbounded_while_loops(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    unbounded = [
        _label(path, n)
        for n in ast.walk(tree)
        if isinstance(n, ast.While) and _is_constant_true(n.test)
    ]
    assert not unbounded, f"'while True' loops need a fixed bound: {unbounded}"
