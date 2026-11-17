"""Regression tests from the 2026-10-25 static sweep (ruff invalid-syntax, F821)."""
import importlib
import shutil
import subprocess
import typing
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_audit_module_is_valid_syntax_on_python_311():
    """pyproject declares requires-python >= 3.10, but a backslash inside an f-string replacement field
    (PEP 701, Python 3.12+) made `import finmodel.audit` a SyntaxError on 3.10/3.11."""
    py311 = shutil.which("python3.11") or shutil.which("python3.10")
    if not py311:
        pytest.skip("no Python 3.10/3.11 interpreter available to check the syntax floor")
    r = subprocess.run([py311, "-I", "-m", "py_compile", str(ROOT / "finmodel" / "audit.py")],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr


def test_audit_markdown_escapes_pipes():
    from finmodel import audit
    res = {"file": "x.xlsx", "sheets": 1, "cells": 1, "formulas": 1, "by_severity": {}, "counts": {},
           "findings": [{"severity": "warning", "sheet": "S", "cell": "A1", "kind": "k", "message": "a|b"}]}
    md = audit.to_markdown(res)
    assert "| a\\|b |" in md


def test_dcf_implied_growth_annotations_resolve():
    """`Optional` was used in the signature of implied_growth without being imported; under
    `from __future__ import annotations` this only surfaces when the hints are evaluated."""
    dcf = importlib.import_module("finmodel.dcf")
    hints = typing.get_type_hints(dcf.implied_growth)
    assert hints["target_price"] == typing.Optional[float]
