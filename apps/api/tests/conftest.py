import os
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def pytest_configure(config):
    config.addinivalue_line("markers", "network: requiere IRSA/S3 en vivo")


def pytest_collection_modifyitems(config, items):
    if os.environ.get("SPHEREX_OFFLINE") == "1":
        skip = pytest.mark.skip(reason="SPHEREX_OFFLINE=1")
        for it in items:
            if "network" in it.keywords:
                it.add_marker(skip)


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES
