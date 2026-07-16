"""
Abstract classes for the Validator Layer.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List

from backend.admin.services.exceptions import ValidationException


class IValidator(ABC):
    """Interface for domain validators."""
    
    @abstractmethod
    def validate(self, data: Any) -> None:
        """
        Validate the data. 
        Raises ValidationException if validation fails.
        """
        pass


class BaseValidator(IValidator):
    """Base validator with helper methods."""
    
    def _add_error(self, errors: List[str], message: str) -> None:
        errors.append(message)
        
    def _raise_if_errors(self, errors: List[str]) -> None:
        if errors:
            raise ValidationException(f"Validation failed: {'; '.join(errors)}")
