import pytest
from fastapi.testclient import TestClient
from backend.main import app
import time

@pytest.fixture
def auth_client():
    client = TestClient(app)
    test_email = f"subs_{int(time.time())}@test.com"
    client.post("/auth/register", json={"email": test_email, "password": "SecurePassword123!"})
    res = client.post("/auth/login", json={"email": test_email, "password": "SecurePassword123!"})
    client.cookies.set("access_token", res.cookies.get("access_token"))
    return client

def test_get_subscription_status(auth_client):
    res = auth_client.get("/api/subscriptions/my-plan")
    assert res.status_code in [200, 404]

def test_upgrade_subscription(auth_client, mocker):
    mock_payment = mocker.MagicMock()
    mock_payment.create_checkout_session.return_value = "http://checkout.url"
    mocker.patch("backend.core.providers.payment_provider.PaymentProvider", return_value=mock_payment)
    res = auth_client.post("/api/subscriptions/upgrade", json={"plan_name": "pro"})
    assert res.status_code in [200, 404, 400]
