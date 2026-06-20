from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "welcome to happy kitchen"}

def test_get_menu():
    response = client.get("/menu")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_invalid_login():
    response = client.post("/login", json={
        "email": "fake@test.com",
        "password": "wrongpass"
    })
    assert response.status_code == 400