

# File: self_evaluate.py
import logging
from self_modify import modify_action_logic
from log_utils import analyze_failures

logger = logging.getLogger()

def self_evaluate(action_success_rates, action_weights):
    """Evaluate the success of each action and adapt decision-making logic."""
    for action, data in action_success_rates.items():
        if data["total"] > 0:
            success_rate = data["positive"] / data["total"]
            logger.info(f"Success rate for {action}: {success_rate:.2f}")
            # If success rate is low, reduce the likelihood of choosing this action
            if success_rate < 0.3:
                logger.info(f"Low success rate detected for {action}. Considering code modification.")
                modify_action_logic(action, action_weights)

    # Analyze failure patterns and adjust accordingly
    failure_patterns = analyze_failures()
    for action, count in failure_patterns.items():
        if count > 3:  # Arbitrary threshold for frequent failures
            logger.info(f"Frequent failure detected for {action}. Considering further modification.")
            modify_action_logic(action, action_weights)
