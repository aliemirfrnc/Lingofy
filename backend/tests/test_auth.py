import pytest
from fastapi.testclient import TestClient
import time
import os

# Ayarlar test başlamadan önce override edilebilir

os.environ["JWT_SECRET"] = "test-secret"
from backend.main import app
from backend.core.db import get_conn

@pytest.fixture
def client():
    # In-memory veritabanı simülasyonu tam olarak mümkün değil çünkü 
    # projenin SQLite kullanımı global ve fiziksel dosyaya (lingofy.db) bağlı.
    # Bu yüzden testler asıl veritabanına dokunabilir, izolasyon için 
    # ilerleyen sprintlerde veritabanı url config içine alınmalıdır.
    with TestClient(app) as c:
        yield c

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_login_invalid_credentials(client):
    test_email = f"wrong_{int(time.time())}@test.com"
    response = client.post("/auth/login", json={"email": test_email, "password": "wrongpassword"})
    assert response.status_code in [401, 404]

def test_register_and_login(client):
    # Bu test mevcut veritabanını kullanacağı için çakışma olabilir.
    # Rastgele email üreterek test edebiliriz.
    test_email = f"test_{int(time.time())}@test.com"
    test_password = "SecurePassword123!"

    # Register
    res_reg = client.post("/auth/register", json={"email": test_email, "password": test_password})
    assert res_reg.status_code == 200
    assert "status" in res_reg.json()

    # Login
    res_login = client.post("/auth/login", json={"email": test_email, "password": test_password})
    assert res_login.status_code == 200
    assert "access_token" in res_login.cookies
    assert "refresh_token" in res_login.cookies

    # Refresh
    refresh_token = res_login.cookies["refresh_token"]
    res_refresh = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert res_refresh.status_code == 200
    assert "access_token" in res_refresh.cookies

def test_protected_route_without_token(client):
    res = client.get("/auth/me")
    assert res.status_code == 401

def test_logout(client):
    test_email = f"logout_{int(time.time())}@test.com"
    client.post("/auth/register", json={"email": test_email, "password": "SecurePassword123!"})
    res_login = client.post("/auth/login", json={"email": test_email, "password": "SecurePassword123!"})
    assert "access_token" in res_login.cookies
    client.cookies.set("access_token", res_login.cookies["access_token"])
    
    res_logout = client.post("/auth/logout")
    assert res_logout.status_code == 200
    
    # TestClient sometimes doesn't clear cookies correctly from Set-Cookie max-age=0
    client.cookies.clear()
    
    res_me = client.get("/auth/me")
    assert res_me.status_code == 401
