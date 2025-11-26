"""Custom exceptions for the DAPERL framework."""

from temporalio.exceptions import ApplicationError
from daperl.core.models import ActionResult


class ActionExecutionError(ApplicationError):
    """
    Exception raised when an action execution fails.
    
    This exception inherits from Temporal's ApplicationError for better
    integration with Temporal's error handling and retry mechanisms.
    It contains the ActionResult with full details about the failure,
    allowing callers to access failure information while still propagating the error.
    
    Attributes:
        action_result: The ActionResult containing failure details
    """
    
    def __init__(self, action_result: ActionResult, non_retryable: bool = True):
        """
        Initialize the exception with an ActionResult.
        
        Args:
            action_result: The result of the failed action execution
            non_retryable: Whether this error should prevent retries (default: True)
        """
        self.action_result = action_result
        super().__init__(
            f"Action {action_result.action_id} failed: {action_result.message}",
            type="ActionExecutionError",
            non_retryable=non_retryable,
        )
