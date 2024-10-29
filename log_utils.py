

# File: log_utils.py
import json
import os

def log_decision(action, outcome, values, api_response=None, context=None):
    log_entry = {
        "action": action,
        "outcome": outcome,
        "values": values,
        "api_response": api_response,
        "context": context
    }

    log_file = "decision_log.json"
    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            log_data = json.load(file)
    else:
        log_data = []

    log_data.append(log_entry)

    with open(log_file, "w") as file:
        json.dump(log_data, file, indent=4)


def analyze_failures():
    """Analyze the log to determine common patterns in failed actions."""
    log_file = "decision_log.json"
    if not os.path.exists(log_file):
        return {}

    with open(log_file, "r") as file:
        log_data = json.load(file)

    failure_patterns = {}
    for entry in log_data:
        if entry["outcome"] == "negative":
            action = entry["action"]
            if action not in failure_patterns:
                failure_patterns[action] = 0
            failure_patterns[action] += 1

    return failure_patterns
