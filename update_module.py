import requests
import logging

# Configure logging
logger = logging.getLogger()

# Comment Analysis Function
def comment_analysis(comment_text, credential, endpoint):
    """Analyze a comment using Azure Text Analytics and return the outcome."""
    
    # Check if the comment is valid
    if not comment_text.strip():  # Validate that comment_text is not empty or just whitespace
        logger.info("Skipped analysis for empty or invalid comment.")
        return "skipped", {"error": "Invalid: Empty Comment"}

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

        # Set the correct scope for the Azure Text Analytics API
        scope = f"{endpoint}/.default"
        headers = {
            "Authorization": f"Bearer {credential.get_token(scope).token}",
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
