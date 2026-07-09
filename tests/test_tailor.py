"""Tests for tailor helpers that don't require a live LLM."""
import json

import pytest

from src.tailor import parse_json


def test_parse_json_plain():
    assert parse_json('{"a": 1}') == {"a": 1}


def test_parse_json_strips_code_fence():
    raw = '```json\n{"a": 1, "b": [2, 3]}\n```'
    assert parse_json(raw) == {"a": 1, "b": [2, 3]}


def test_parse_json_strips_bare_fence():
    raw = '```\n{"ok": true}\n```'
    assert parse_json(raw) == {"ok": True}


def test_parse_json_handles_leading_whitespace():
    assert parse_json('   {"x": "y"}   ') == {"x": "y"}


def test_parse_json_raises_on_garbage():
    with pytest.raises(json.JSONDecodeError):
        parse_json("this is not json")
