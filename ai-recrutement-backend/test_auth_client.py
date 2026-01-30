from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

email = "debug_test@example.com"
password = "imanita2004"
role = "candidat"

print("== Registering user ==")
resp = client.post("/api/auth/register", json={
    "email": email,
    "password": password,
    "role": role,
    "nom": "Debug User"
})
print(resp.status_code)
try:
    print(resp.json())
except Exception as e:
    print("No JSON response", e)

print("== Logging in ==")
resp = client.post("/api/auth/login", json={"email": email, "password": password})
print(resp.status_code)
print(resp.json())

if resp.status_code == 200:
    token = resp.json().get("access_token")
    print("Access token:", token)
    headers = {"Authorization": f"Bearer {token}"}
    print("== Calling /api/auth/me with Authorization header ==")
    r = client.get("/api/auth/me", headers=headers)
    print(r.status_code)
    try:
        print(r.json())
    except Exception as e:
        print("No JSON", e)
else:
    print("Login failed; cannot call /me")
