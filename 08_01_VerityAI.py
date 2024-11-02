import logging
import json
import os
import random
import requests
import subprocess
from azure.identity import AzureCliCredential
from azure.keyvault.secrets import SecretClient
from ai_decision import decide_action
from feedback import evaluate_feedback  # Ensure this is included
from log_utils import log_decision  # Ensure this is includedfrom self_modify import modify_action_logic, commit_and_push_changes

import subprocess


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

# Define action_weights (ensure this aligns with your AI logic)
action_weights = {
    'tell_truth': 1.0,
    'be_benevolent': 1.0,
    'be_tolerant': 1.0,
    'analyze_comment': 1.0,
}

# ... rest of your code ...


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Define action_weights (ensure this aligns with your AI logic)
action_weights = {
    'tell_truth': 1.0,
    'be_benevolent': 1.0,
    'be_tolerant': 1.0,
    'analyze_comment': 1.0,
}

# Set up Azure Key Vault to fetch API key
key_vault_name = "VerityAIVault"  # Replace with your Key Vault name
key_vault_uri = f"https://{key_vault_name}.vault.azure.net/"
credential = AzureCliCredential()  # Use Azure CLI for authentication
client = SecretClient(vault_url=key_vault_uri, credential=credential)

# Fetch API key from Azure Key Vault
secret_name = "AZURE-CLIENT-ID"
try:
    api_key = client.get_secret(secret_name).value
    logger.info("Successfully retrieved API key from Key Vault.")
except Exception as e:
    logger.error(f"Failed to retrieve API key: {e}")
    raise

# Set up Azure Text Analytics endpoint
endpoint = "https://verityai.cognitiveservices.azure.com"  # Replace with your actual endpoint
url = f"{endpoint}/text/analytics/v3.0/sentiment"

# Load memory from a JSON file if it exists
memory_file = "memory.json"
if os.path.exists(memory_file):
    with open(memory_file, "r") as file:
        memory = json.load(file)  # Load existing memory
else:
    memory = []  # Initialize memory as an empty list



def commit_and_push_changes():
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Automated code modification"])
    subprocess.run(["git", "push"])



def self_evaluate(action_success_rates, action_weights):
    # Existing logic for evaluating actions...
    # Call modify_action_logic() when needed

    # After modifications
    commit_and_push_changes()

    
# Autonomous Loop with Comment Analysis
def autonomous_loop():
    """The main loop where AI makes decisions, analyzes comments, and adjusts based on outcomes."""
    for _ in range(5):
        action = decide_action(action_weights)  # Ensure action_weights is defined
        print(f"AI decided to: {action}")

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
        log_decision(action, outcome, VALUES.copy(), api_response=result)

        print(f"Current Values: {VALUES}\n")

    # Self-evaluate after completing actions
    self_evaluate(action_success_rates, action_weights)

    # Save memory to a JSON file
    with open(memory_file, "w") as file:
        json.dump(memory, file)

# Run the autonomous loop
if __name__ == "__main__":
    autonomous_loop()
