import logging
import json
import os
import random
import requests
import subprocess
import warnings
import sys
import contextlib

from azure.identity import AzureCliCredential
from azure.keyvault.secrets import SecretClient
from ai_decision import decide_action
from feedback import evaluate_feedback
from log_utils import log_decision
from self_modify import modify_action_logic, commit_and_push_changes

# Capture and log warnings
def warn_on_warnings(message, category, filename, lineno, file=None, line=None):
    logger.warning(f"Warning: {message} (category: {category.__name__}, filename: {filename}, line: {lineno})")

# Attach the warning function to display warnings
warnings.showwarning = warn_on_warnings

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

# Define action_weights
action_weights = {
    'tell_truth': 1.0,
    'be_benevolent': 1.0,
    'be_tolerant': 1.0,
    'analyze_comment': 1.0,
}

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set to INFO to see warnings
logger = logging.getLogger()

# Set up Azure Key Vault to fetch API key
key_vault_name = "VerityAIVault"
key_vault_uri = f"https://{key_vault_name}.vault.azure.net/"
credential = AzureCliCredential()
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
endpoint = "https://verityai.cognitiveservices.azure.com"
url = f"{endpoint}/text/analytics/v3.0/sentiment"

# Load memory from a JSON file if it exists
memory_file = "memory.json"
if os.path.exists(memory_file):
    with open(memory_file, "r") as file:
        memory = json.load(file)
else:
    memory = []

def search_information(query):
    """Search for information on the web using DuckDuckGo."""
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    response = requests.get(url)
    return response.json()

def commit_and_push_changes():
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Automated code modification"])
    subprocess.run(["git", "push"])

def self_evaluate(action_success_rates, action_weights):
    commit_and_push_changes()

# Autonomous Loop with Comment Analysis
# Autonomous Loop with Comment Analysis
def autonomous_loop():
    """The main loop where AI makes decisions, analyzes comments, and adjusts based on outcomes."""
    while True:  # Run continuously
        info = search_information("latest trends in AI")
        print("Retrieved Information:", info)

        action = decide_action(action_weights)
        print(f"AI decided to: {action}")

        if action == "analyze_comment":
            comments_to_analyze = ["hello", "how are you?", "this is great!", "not good", "ciao..."]
            for comment_text in comments_to_analyze:
                print(f"Analyzing comment: {comment_text}")

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

                print(f"Outcome of action: {outcome}")
                memory.append((action, outcome))
                evaluate_feedback(action, outcome, VALUES, action_success_rates)

                log_decision(action, outcome, VALUES.copy(), api_response=result)

                print(f"Current Values: {VALUES}\n")

                self_evaluate(action_success_rates, action_weights)

                with open(memory_file, "w") as file:
                    json.dump(memory, file)

# Run the autonomous loop
if __name__ == "__main__":
    autonomous_loop()
