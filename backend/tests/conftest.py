from __future__ import annotations

import os

import pytest

from app.config import settings


@pytest.fixture(autouse=True)
def disable_api_key_auth_for_tests(monkeypatch):
    """
    Keep API-key middleware available in runtime, but make pytest deterministic.

    Some local shells export PROMETEO_API_KEY for real backend usage.
    Without this fixture, tests that intentionally call internal endpoints
    through TestClient without headers fail with 401.
    """
    monkeypatch.setenv("PROMETEO_API_KEY", "")
    settings.prometeo_api_key = ""
    yield
