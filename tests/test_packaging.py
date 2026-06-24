"""Guard the declared Python support against the #1 regression.

The package uses PEP 585 generics (``list[str]``, ``set[...]``) which are only
importable on Python >= 3.9, so the advertised support must not claim anything
older.
"""
import configparser
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIN_PYTHON = (3, 9)


def _parse_py_envs(envlist):
    versions = []
    for env in re.split(r"[,\s]+", envlist.strip()):
        match = re.fullmatch(r"py(\d)(\d+)", env)
        if match:
            versions.append((int(match.group(1)), int(match.group(2))))
    return versions


def test_tox_targets_supported_pythons_only():
    cfg = configparser.ConfigParser()
    cfg.read(ROOT / "tox.ini")
    versions = _parse_py_envs(cfg["tox"]["envlist"])
    assert versions, "no py environments found in tox.ini"
    assert min(versions) >= MIN_PYTHON, f"tox.ini targets unsupported Python {min(versions)}"


def test_pyproject_requires_python_matches_floor():
    text = (ROOT / "pyproject.toml").read_text()
    match = re.search(r"""requires-python\s*=\s*["']>=\s*(\d+)\.(\d+)["']""", text)
    assert match, "requires-python not found in pyproject.toml"
    assert (int(match.group(1)), int(match.group(2))) == MIN_PYTHON
