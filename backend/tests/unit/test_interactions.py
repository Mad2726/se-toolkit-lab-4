import os

import httpx

from app.models.interaction import InteractionLog
from app.routers.interactions import filter_by_max_item_id


def _base_url() -> str:
    # Works locally + in CI. Prefer explicit env var if your harness sets one.
    return os.getenv("E2E_BASE_URL", os.getenv("API_BASE_URL", "http://localhost:8000")).rstrip("/")


def test_get_interactions_returns_200() -> None:
    resp = httpx.get(f"{_base_url()}/interactions/", timeout=10.0)
    assert resp.status_code == 200


def test_get_interactions_response_items_have_expected_fields() -> None:
    resp = httpx.get(f"{_base_url()}/interactions/", timeout=10.0)
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0  # e2e env is expected to have seed data

    for item in data:
        assert "id" in item
        assert "item_id" in item
        assert "created_at" in item


def test_get_interactions_filter_includes_boundary() -> None:
    resp = httpx.get(f"{_base_url()}/interactions/", params={"max_item_id": 1}, timeout=10.0)
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0

    for item in data:
        assert int(item["item_id"]) <= 1

"""Unit tests for interaction filtering logic."""


def _make_log(id: int, learner_id: int, item_id: int) -> InteractionLog:
    return InteractionLog(id=id, learner_id=learner_id, item_id=item_id, kind="attempt")


def test_filter_returns_all_when_max_item_id_is_none() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=None)
    assert result == interactions


def test_filter_returns_empty_for_empty_input() -> None:
    result = filter_by_max_item_id(interactions=[], max_item_id=1)
    assert result == []


def test_filter_returns_interactions_below_max() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 3)]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=2)
    assert len(result) == 1
    assert result[0].id == 1

def test_filter_excludes_interaction_with_different_learner_id():
    from app.routers.interactions import _filter_by_item_id
    from types import SimpleNamespace

    interactions = [
        SimpleNamespace(item_id=1),
        SimpleNamespace(item_id=2),
    ]

    result = _filter_by_item_id(interactions, 1)

    assert len(result) == 1
    assert result[0].item_id == 1


