
# File: feedback.py
def evaluate_feedback(action, outcome, values, action_success_rates):
    """Adjust value scores based on the feedback received."""
    action_map = {
        "tell_truth": "truth",
        "be_benevolent": "benevolence",
        "be_tolerant": "tolerance"
    }

    value_key = action_map.get(action)
    if value_key:
        if outcome == "positive":
            values[value_key] += 0.1
            action_success_rates[action]["positive"] += 1
        elif outcome == "negative":
            values[value_key] -= 0.1

        action_success_rates[action]["total"] += 1
        values[value_key] = max(0, min(1, values[value_key]))
