import pytest
from backend.admin.services.notification.providers import (
    INotificationProvider,
    IEmailProvider,
    IWebhookProvider,
    ISlackProvider,
    IInAppProvider
)

class MockEmailProvider(IEmailProvider):
    def send(self, recipient: str, subject: str, message: str, payload: dict = None) -> bool:
        return True

class MockWebhookProvider(IWebhookProvider):
    def send(self, recipient: str, subject: str, message: str, payload: dict = None) -> bool:
        return True

class MockSlackProvider(ISlackProvider):
    def send(self, recipient: str, subject: str, message: str, payload: dict = None) -> bool:
        return True

class MockInAppProvider(IInAppProvider):
    def send(self, recipient: str, subject: str, message: str, payload: dict = None) -> bool:
        return True

def test_email_provider_interface():
    provider = MockEmailProvider()
    assert isinstance(provider, INotificationProvider)
    assert provider.send("test@test.com", "Sub", "Msg") is True

def test_webhook_provider_interface():
    provider = MockWebhookProvider()
    assert isinstance(provider, INotificationProvider)
    assert provider.send("https://hook.local", "Sub", "Msg", {"id": 1}) is True

def test_slack_provider_interface():
    provider = MockSlackProvider()
    assert isinstance(provider, INotificationProvider)
    assert provider.send("#general", "Alert", "App is down") is True

def test_inapp_provider_interface():
    provider = MockInAppProvider()
    assert isinstance(provider, INotificationProvider)
    assert provider.send("user_123", "Welcome", "Welcome to Lingofy") is True
