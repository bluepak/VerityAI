
# File: main.py
import logging
import json
import os
import requests
import random
from ai_decision import decide_action
from feedback import evaluate_feedback
from log_utils import log_decision
from self_evaluate import self_evaluate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Set up Azure Text Analytics API key and endpoint
endpoint = "https://verityai.cognitiveservices.azure.com"  # Replace with your actual endpoint
url = f"{endpoint}/text/analytics/v3.0/sentiment"

# Core Values
VALUES = {
    "truth": 1.0,
    "benevolence": 1.0,
    "tolerance": 1.0
}

# Track the success rate of each action
action_success_rates = {
    "tell_truth": {"positive": 0, "total": 0},
    "be_benevolent": {"positive": 0, "total": 0},
    "be_tolerant": {"positive": 0, "total": 0}
}

# Weights for each action
action_weights = {
    "tell_truth": 1.0,
    "be_benevolent": 1.0,
    "be_tolerant": 1.0,
    "analyze_comment": 1.0
}

# Load memory from a JSON file if it exists
memory_file = "memory.json"
if os.path.exists(memory_file):
    with open(memory_file, "r") as file:
        memory = json.load(file)
else:
    memory = []

# Autonomous Loop with Comment Analysis
def autonomous_loop():
    """The main loop where AI makes decisions, analyzes comments, and adjusts based on outcomes."""
    for _ in range(5):
        action = decide_action(action_weights)
        print(f"AI decided to: {action}")

        context = {
            "previous_values": VALUES.copy(),
            "previous_action": memory[-1][0] if memory else None,
            "previous_outcome": memory[-1][1] if memory else None
        }

        if action == "analyze_comment":
            comment_text = input("Enter the comment text to analyze: ")

            # Prepare the request body
            analyze_request = {
                "documents": [
                    {
                        "id": "1",
                        "language": "en",
                        "text": comment_text
                    }
                ]
            }

            headers = {
                "Ocp-Apim-Subscription-Key": api_key,
                "Content-Type": "application/json"
            }

            # Make the API request
            try:
                response = requests.post(url, headers=headers, json=analyze_request)
                response.raise_for_status()
                result = response.json()
                logger.info("API Response: %s", result)
                outcome = "positive"
            except requests.exceptions.RequestException as e:
                logger.error("Request failed: %s", e)
                result = None
                outcome = "negative"
        else:
            outcome = random.choice(["positive", "negative"])
            result = None
            print(f"Outcome of action: {outcome}")

        memory.append((action, outcome))
        evaluate_feedback(action, outcome, VALUES, action_success_rates)

        # Log the decision and result to the JSON file
        log_decision(action, outcome, VALUES.copy(), api_response=result, context=context)

        print(f"Current Values: {VALUES}\n")

    # Self-evaluate after completing actions
    self_evaluate(action_success_rates, action_weights)

    # Save memory to a JSON file
    with open(memory_file, "w") as file:
        json.dump(memory, file)

# Run the autonomous loop
autonomous_loop()
