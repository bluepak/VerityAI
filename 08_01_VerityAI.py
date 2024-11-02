import logging
import json
import os
import random
import requests
import subprocess
import warnings
import time
import re



from datetime import datetime

from azure.identity import AzureCliCredential
from azure.keyvault.secrets import SecretClient
from ai_decision import decide_action
from feedback import evaluate_feedback
from log_utils import log_change, log_decision
from self_modify import modify_action_logic, commit_and_push_changes
from update_module import comment_analysis
from collections import Counter


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

def generate_dynamic_query(keywords):
    """Generate a dynamic and unique search query each time."""
    import random

    # Common AI-related phrases for variation
    additional_phrases = ["latest insights", "trending", "developments in", "future of"]
    # Filter out any single characters or empty strings to prevent fragmentation
    cleaned_keywords = [keyword.strip() for keyword in keywords if len(keyword.strip()) > 1]

    # Join cleaned keywords into a base query
    base_query = " ".join(cleaned_keywords)

    # Add a random phrase for variety
    query_with_phrase = f"{random.choice(additional_phrases)} {base_query}"

    # Split the query into words, shuffle, and reassemble to maintain readability
    keyword_list = query_with_phrase.split()
    random.shuffle(keyword_list)
    
    # Join the shuffled list into a single query string
    final_query = " ".join(keyword_list)
    
    # Log to verify the output structure
    print("Generated Search Query:", final_query)
    
    return " ".join(keyword_list)


def detect_patterns(text_data):
    """Identify recurring keywords or topics from provided text data."""
    # Convert text to lowercase and remove non-alphanumeric characters
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text_data.lower())
    words = cleaned_text.split()

    # Count word occurrences
    common_words = Counter(words)

    # Filter out common stop words and select frequent keywords
    stop_words = {"the", "is", "and", "in", "to", "of", "a", "for", "you", "this", "are", "how"}
    keywords = {word: count for word, count in common_words.items() if word not in stop_words and count > 1}

    return list(keywords.keys())  # Return a list of keywords




# Sample data for testing pattern detection
sample_text = "hello how are you this is great not good hello AI is amazing AI trends future AI hello"

# Run the detect_patterns function to extract keywords
keywords = detect_patterns(sample_text)
print("Extracted Keywords:", keywords)  # Should print out a list of keywords based on frequency


def log_change(description, module):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"Change: {description} | Module: {module} | Time: {timestamp}")




# Sample data for testing pattern detection
sample_text = "hello how are you this is great not good hello AI is amazing AI trends future AI hello"

# Run the detect_patterns function to extract keywords
keywords = detect_patterns(sample_text)
print("Extracted Keywords:", keywords)

import requests

def search_information(keywords):
    """Search for information on the web using extracted keywords with error handling."""
    query = generate_dynamic_query(keywords)  # Create a search query from the keywords
    url = f"https://api.duckduckgo.com/?q={query}&format=json"  # Replace with actual API if needed

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        print("Search Query:", query)  # Log the dynamic search query
        
        # Attempt to parse the JSON response
        try:
            return response.json()
        except ValueError:
            print("Error: Response is not in JSON format or is empty.")
            return {}  # Return an empty dictionary if JSON parsing fails

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return {}  # Return an empty dictionary on request failure



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
def detect_patterns(text_data):
    """Identify recurring keywords or topics from provided text data."""
    # Convert text to lowercase and remove non-alphanumeric characters
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text_data.lower())
    words = cleaned_text.split()

    # Count word occurrences
    common_words = Counter(words)

    # Filter out common stop words and select frequent keywords
    stop_words = {"the", "is", "and", "in", "to", "of", "a", "for"}  # Add more as needed
    keywords = {word: count for word, count in common_words.items() if word not in stop_words and count > 1}

    return list(keywords.keys())  # Return a list of keywords


def get_recent_data():
    """Fetches recent data for pattern detection, such as logs or comments."""
    # Replace with the actual source of data (e.g., reading from a log file)
    try:
        with open("recent_data.txt", "r") as file:  # Example file with recent interactions
            data = file.read()
    except FileNotFoundError:
        data = "No recent data available."

    return data


import datetime  # Make sure this is imported at the top of your script

def autonomous_loop():
    """The main loop where AI makes decisions, analyzes comments, and adjusts based on outcomes."""
    loop_counter = 1  # Initialize a counter for the loop iterations
    while True:  # Run continuously
        # Add timestamp and loop message
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d") + f"_{now.hour}_{now.minute}{'a' if now.hour < 12 else 'p'}_MT"
        print(f"{timestamp} - Starting loop #{loop_counter}")


        # Replace sample_text with real data input (e.g., from logs or live comments)
        recent_data = get_recent_data()  # Function to fetch updated comments or logs
        keywords = detect_patterns(recent_data)

        if keywords:
            info = search_information(keywords)
            print("Retrieved Information:", info)
        
        # Existing actions and logic...

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


        # Sample comments for testing
        comments = "hello how are you this is great not good hello AI trends future AI hello"
        
        # Extract keywords from comments
        keywords = detect_patterns(comments)
        
        # Perform a dynamic search using the extracted keywords
        if keywords:
            info = search_information(keywords)
            print("Retrieved Information:", info)

        loop_counter += 1  # Increment the loop counter
        time.sleep(7)  # Optional: Pause for 60 seconds before the next iteration

# Run the autonomous loop
if __name__ == "__main__":
    autonomous_loop()
