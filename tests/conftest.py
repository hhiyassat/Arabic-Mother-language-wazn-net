"""conftest — جذر المستودع على المسار + fixtures."""
import pytest

from tests._pilot import PILOT, PILOT_ROOTS  # noqa: F401  (يضع جذر المستودع على sys.path)


@pytest.fixture(scope="session")
def pilot():
    return PILOT


@pytest.fixture(scope="session")
def pilot_roots():
    return PILOT_ROOTS
