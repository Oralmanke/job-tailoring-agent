"""Test setup shared by all tests.

``src.config.Settings`` requires DB_URL and reads it at import time, so we set
dummy environment values here (before any ``src`` module is imported) to keep
unit tests self-contained and independent of a real database or API keys.
"""
import os

os.environ.setdefault("DB_URL", "postgresql://test:test@localhost:5432/testdb")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("ADZUNA_APP_ID", "test-id")
os.environ.setdefault("ADZUNA_APP_KEY", "test-key")
