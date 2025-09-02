# File: ai_decision.py
import random

def decide_action(action_weights):
    """Select an action based on a mapping of weights.

    Args:
        action_weights (dict): Mapping of action names to selection weights.

    Returns:
        str: The chosen action.

    Raises:
        ValueError: If ``action_weights`` is empty.
    """
    if not action_weights:
        raise ValueError("action_weights must not be empty")

    actions = list(action_weights.keys())
    weights = list(action_weights.values())
    return random.choices(actions, weights=weights, k=1)[0]
