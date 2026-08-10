"""Tests for what the built distribution contains.

`poetry install` puts the source tree on the path, so `fragment/py.typed` is
found whether or not the build is configured to ship it. Only the built wheel
shows what a customer gets, and without the marker a type checker skips the
installed package entirely -- every call into the SDK goes unchecked, and the
typed batch payloads become decoration.

Offline; needs poetry on PATH.
"""

import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
MARKER = "fragment/py.typed"

pytestmark = pytest.mark.skipif(
    shutil.which("poetry") is None, reason="needs poetry to build the wheel"
)


@pytest.fixture(scope="module")
def wheel(tmp_path_factory: pytest.TempPathFactory) -> Path:
    output = tmp_path_factory.mktemp("dist")
    subprocess.run(
        ["poetry", "build", "--format", "wheel", "--output", str(output)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    built = list(output.glob("*.whl"))
    assert len(built) == 1, built
    return built[0]


def test_the_marker_file_exists_in_the_source_tree() -> None:
    assert (REPO_ROOT / MARKER).is_file()


def test_the_wheel_ships_the_marker(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        assert MARKER in archive.namelist(), archive.namelist()[:20]


def test_the_wheel_ships_both_sdks(wheel: Path) -> None:
    """A marker only helps for modules that are actually packaged."""
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
    assert "fragment/sdk/typed_entries.py" in names
    assert "fragment/sync_sdk/typed_entries.py" in names
