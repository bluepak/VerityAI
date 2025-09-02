"""Tests for the ai_decision module."""

import pytest

from ai_decision import decide_action


def test_decide_action_returns_valid_action():
    """The returned action should be one of the provided keys."""
    weights = {"a": 1, "b": 2, "c": 3}
    action = decide_action(weights)
    assert action in weights


def test_decide_action_empty_weights():
    """An empty mapping should raise a ValueError."""
    with pytest.raises(ValueError):
        decide_action({})

