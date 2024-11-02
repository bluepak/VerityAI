import logging
import random
import subprocess

logger = logging.getLogger()

def modify_action_logic(action, action_weights):
    """Modify the decision-making logic to improve the success rate of the given action."""
    logger.info(f"Modifying logic for action: {action}")
    if action in action_weights:
        new_weight = action_weights[action] * random.uniform(0.1, 0.5)  # Reduce weight to make it less likely
        action_weights[action] = new_weight
        logger.info(f"New weight for {action}: {new_weight}")

def commit_and_push_changes():
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Automated code modification"])
    subprocess.run(["git", "push"])
