import logging
import json
import os
import random
import requests
import subprocess
import warnings
import time
from datetime import datetime

from azure.identity import AzureCliCredential
from azure.keyvault.secrets import SecretClient
from ai_decision import decide_action
from feedback import evaluate_feedback
from log_utils import log_change, log_decision
from self_modify import modify_action_logic, commit_and_push_changes
from update_module import comment_analysis


# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Capture and log warnings
def warn_on_warnings(message, category, filename, lineno, file=None, line=None):
    logger.warning(f"Warning: {message} (category: {category.__name__}, filename: {filename}, line: {lineno})")

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



# Initialize logging
logging.basicConfig(filename='verityai_changes.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def log_change(description, module):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"Change: {description} | Module: {module} | Time: {timestamp}")


def search_information(query):
    """Search for information on the web using DuckDuckGo."""
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    response = requests.get(url)
    return response.json()
def commit_and_push_changes():
    # Get the list of changes to be committed
    result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
    changes = result.stdout.strip()
    
    if changes:
        # Commit the changes
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "Automated code modification"])
        subprocess.run(["git", "push"])

        # Display the changes in the output
        print("--------------------")
        print("Updating my code to:")
        print(changes)  # Display the code changes
        print("Because: Automated code modification")
        print("--------------------")
    else:
        print("No changes to commit.")

def infer_reason(changes):
    if "added" in changes or "new" in changes:
        return "Adding new features."
    elif "removed" in changes or "deleted" in changes:
        return "Removing unnecessary code."
    elif "fix" in changes or "error" in changes:
        return "Fixing identified issues."
    else:
        return "General code modifications."


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def commit_and_push_changes(reason="Automated code modification"):
    # Get the diff of the changes
    diff = subprocess.run(["git", "diff"], capture_output=True, text=True)
    
    # If there are changes, proceed to commit
    if diff.stdout:
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", reason])
        subprocess.run(["git", "push"])

        # Log the changes
        logger.info("Committed changes:\n%s", diff.stdout)
        logger.info("Reason for changes: %s", reason)
    else:
        logger.info("No changes to commit.")



def self_evaluate(action_success_rates, action_weights):
    commit_and_push_changes()

# Autonomous Loop with Comment Analysis

import datetime  # Make sure this is imported at the top of your script

def autonomous_loop():
    """The main loop where AI makes decisions, analyzes comments, and adjusts based on outcomes."""
    loop_counter = 1  # Initialize a counter for the loop iterations
    while True:  # Run continuously
        # Add timestamp and loop message
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d") + f"_{now.hour}_{now.minute}{'a' if now.hour < 12 else 'p'}_MT"
        print(f"{timestamp} - Starting loop #{loop_counter}")

        # Existing code follows...
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

        loop_counter += 1  # Increment the loop counter
        time.sleep(17)  # Optional: Pause for 60 seconds before the next iteration

# Run the autonomous loop
if __name__ == "__main__":
    autonomous_loop()
