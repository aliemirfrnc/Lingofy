"""
Provider Interfaces for the Notification domain.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class INotificationProvider(ABC):
    """Base interface for all notification providers."""
    
    @abstractmethod
    def send(self, recipient: str, subject: str, message: str, payload: Dict[str, Any] = None) -> bool:
        """Send a notification. Returns True if successful."""
        pass


class IEmailProvider(INotificationProvider):
    """Interface for Email notifications."""
    pass


class IWebhookProvider(INotificationProvider):
    """Interface for Webhook notifications."""
    pass


class ISlackProvider(INotificationProvider):
    """Interface for Slack notifications."""
    pass


class IInAppProvider(INotificationProvider):
    """Interface for In-App notifications."""
    pass
