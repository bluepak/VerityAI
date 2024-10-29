import requests
import logging

# Configure logging
logger = logging.getLogger()

# Comment Analysis Function
def comment_analysis(comment_text, credentials, endpoint):
    """Analyze a comment using Azure Text Analytics and return the outcome."""
    try:
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
            "Authorization": f"Bearer {credentials.get_token().token}",
            "Content-Type": "application/json"
        }

        # Make the API request
        response = requests.post(f"{endpoint}/text/analytics/v3.1/sentiment", headers=headers, json=analyze_request)
        response.raise_for_status()
        result = response.json()
        logger.info("API Response: %s", result)

        # Return positive if sentiment score is above neutral threshold
        if result['documents'][0]['sentiment'] == 'positive':
            return "positive", result
        else:
            return "negative", result

    except requests.exceptions.RequestException as e:
        logger.error("Request failed: %s", e)
        return "negative", None

# Core Value Update Function
def update_core_values(action, outcome, VALUES):
    """Adjust value scores based on the feedback received."""
    # Map actions to core values
    action_map = {
        "tell_truth": "truth",
        "be_benevolent": "benevolence",
        "be_tolerant": "tolerance"
    }

    # Get the corresponding value key
    value_key = action_map.get(action)
    if value_key:
        if outcome == "positive":
            VALUES[value_key] += 0.1
        elif outcome == "negative":
            VALUES[value_key] -= 0.1

        # Keep values between 0 and 1
        VALUES[value_key] = max(0, min(1, VALUES[value_key]))
