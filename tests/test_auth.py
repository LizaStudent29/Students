def test_register_success(client):
    response = client.post("/auth/register", json={"username": "alice", "password": "123"})
    assert response.status_code == 200
    assert response.json()["message"] == "User registered"

def test_register_duplicate(client):
    client.post("/auth/register", json={"username": "bob", "password": "secret"})
    response = client.post("/auth/register", json={"username": "bob", "password": "secret"})
    assert response.status_code == 400

def test_login_success(client):
    client.post("/auth/register", json={"username": "user", "password": "pass"})
    response = client.post("/auth/token", data={"username": "user", "password": "pass"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "user2", "password": "pass"})
    response = client.post("/auth/token", data={"username": "user2", "password": "wrong"})
    assert response.status_code == 400

