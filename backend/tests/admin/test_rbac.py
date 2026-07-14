import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.db import get_conn

def test_admin_ping_unauthorized(client):
    res = client.get("/api/admin/ping")
    assert res.status_code == 401

def test_admin_ping_forbidden(client):
    client.post("/auth/register", json={"email": "normal@test.com", "password": "Password123!"})
    res_login = client.post("/auth/login", json={"email": "normal@test.com", "password": "Password123!"})
    token = res_login.cookies.get("access_token")
    if not token:
        # maybe it's in the json payload if not cookie only
        pass
    
    res = client.get("/api/admin/ping", cookies={"access_token": token} if token else {})
    if not token:
        res = client.get("/api/admin/ping", headers={"Authorization": f"Bearer {res_login.json().get('access_token')}"})
    assert res.status_code == 403

def test_admin_ping_success(client):
    client.post("/auth/register", json={"email": "admin@test.com", "password": "Password123!"})
    
    conn = get_conn()
    with conn:
        conn.execute("UPDATE users SET role = 'SUPER_ADMIN' WHERE email = 'admin@test.com'")
        
    res_login = client.post("/auth/login", json={"email": "admin@test.com", "password": "Password123!"})
    token = res_login.cookies.get("access_token")
    
    if token:
        res = client.get("/api/admin/ping", cookies={"access_token": token})
    else:
        res = client.get("/api/admin/ping", headers={"Authorization": f"Bearer {res_login.json().get('access_token')}"})
        
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
