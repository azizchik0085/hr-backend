import requests

def test_api():
    try:
        # 1. Login to get token
        login_resp = requests.post("http://localhost:8000/token", data={
            "username": "direktor",
            "password": "123"
        })
        if login_resp.status_code != 200:
            print("Login failed!", login_resp.text)
            return
            
        token = login_resp.json()["access_token"]
        
        # 2. Add branch
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        add_resp = requests.post("http://localhost:8000/branches/", headers=headers, json={
            "name": "API Test Branch",
            "address": "API Test Address"
        })
        
        print(f"Status: {add_resp.status_code}")
        print(f"Body: {add_resp.text}")
        
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_api()
