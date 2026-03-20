import requests

base_url = "https://hr-backend-a75s.onrender.com"

print("Fetching OpenAPI schema from Render...")
r = requests.get(f"{base_url}/openapi.json")

if r.status_code == 200:
    data = r.json()
    paths = data.get("paths", {})
    if "/orders/" in paths:
        print("Muvaffaqiyat: /orders/ endpointi Renderda MAVJUD!")
        print("POST metodlari:", paths["/orders/"].keys())
    else:
        print("XATOLIK: /orders/ endpointi Renderda MAVJUD EMAS!")
        print("Hozir dagi hamma endpointlar ro'yxati:")
        for p in paths.keys():
            print(" -", p)
else:
    print(f"XATOLIK: Server openapi.json ni qaytarmadi. Code: {r.status_code}")
