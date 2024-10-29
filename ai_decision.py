

# File: ai_decision.py
import random

def decide_action(action_weights):
    """Make a decision based on core values and previous experiences."""
    actions = list(action_weights.keys())
    weights = list(action_weights.values())
    return random.choices(actions, weights=weights, k=1)[0]