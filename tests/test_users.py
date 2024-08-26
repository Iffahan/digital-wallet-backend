from fastapi.testclient import TestClient
from digital_wallet.main import create_app

# Create a TestClient instance with the FastAPI app
client = TestClient(create_app())

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Digital Wallet API"}

def test_create_user():
    response = client.post("/users/create", json={
        "email": "admin@email.local",
        "username": "admin",
        "first_name": "Firstname",
        "last_name": "Lastname",
        "password": "password"
    })
    
    assert response.status_code == 200  # Or another appropriate status code

