import requests
import json

url = "http://127.0.0.1:8000/api/v1/whatsapp-catalog"

payload = {
    "sender": "6281234567890",
    "message": "Halo min, gue mau masukin data jualan nih. Namanya Nasi Goreng Gila Gondrong, posisinya ada di perempatan Blok M. Jualannya ada nasi goreng gila, mie goreng gila, sama kwetiau. Yang bikin beda tuh porsinya kuli banget dan pedesnya nampol."
}

headers = {
    "Content-Type": "application/json"
}

print("Sending simulated WhatsApp message to the AI Webhook...\n")

try:
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print("✅ Success! Here is the extracted JSON data:")
        print(json.dumps(response.json(), indent=4))
    else:
        print(f"❌ Failed with Status Code: {response.status_code}")
        print("Error Details:", response.text)

except requests.exceptions.ConnectionError:
    print("❌ Error: Could not connect to the server. Is Uvicorn running?")