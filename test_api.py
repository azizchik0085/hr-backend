import requests

base_url = "https://hr-backend-a75s.onrender.com"

# Login to get token
r_login = requests.post(f"{base_url}/token", data={"username": "admin", "password": "123"})
if r_login.status_code != 200:
    print("Login failed:", r_login.text)
    exit()

token = r_login.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# Create Order Payload exactly as Flutter toJson() output
payload = {
  "customerName": "Testjon",
  "customerPhone": "+998901234567",
  "deliveryAddress": "Tashkent",
  "latitude": None,
  "longitude": None,
  "totalAmount": 150000.0,
  "status": "readyForDelivery",
  "creatorId": "admin-id-123",
  "assignedDeliveryId": None,
  "productImage": None,
  "receiptImage": None,
  "items": []
}

r_post = requests.post(f"{base_url}/orders/", json=payload, headers=headers)
print("POST STATUS:", r_post.status_code)
print("POST ERROR:", r_post.text)
