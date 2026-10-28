
import requests

URL = "http://127.0.0.1:5000/api/buy"

# Both requests use the SAME key
headers = {
    "Idempotency-Key": "duplicate-test-001"
}

print("First request:")
r1 = requests.post(URL, headers=headers, timeout=30)
print("Status:", r1.status_code)
print("Response:", r1.text)

print("\nSecond request with the SAME key:")
r2 = requests.post(URL, headers=headers, timeout=30)
print("Status:", r2.status_code)
print("Response:", r2.text)
