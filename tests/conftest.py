import os
from collections.abc import Generator

import pytest

# CRITICAL: Set before any Pygame import anywhere in the test suite.
# This must be at module level, not inside a fixture, because Pygame
# may be imported at collection time by test modules.
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame  # must follow env var setup above


@pytest.fixture(scope="session", autouse=True)
def _pygame_session() -> Generator[None]:  # pyright: ignore[reportUnusedFunction]
    """Initialize Pygame once for the entire test session, then quit."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def default_7() -> list[int]:
    return [4, 7, 2, 6, 1, 5, 3]


@pytest.fixture
def reverse_7() -> list[int]:
    return [7, 6, 5, 4, 3, 2, 1]


@pytest.fixture
def sorted_7() -> list[int]:
    return [1, 2, 3, 4, 5, 6, 7]


@pytest.fixture
def duplicates_7() -> list[int]:
    return [3, 1, 3, 2, 1, 2, 3]


@pytest.fixture
def single_1() -> list[int]:
    return [1]


@pytest.fixture
def empty_0() -> list[int]:
    return []
