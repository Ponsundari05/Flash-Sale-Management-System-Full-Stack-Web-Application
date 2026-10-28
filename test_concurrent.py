
import concurrent.futures
import requests
import uuid

URL = "http://127.0.0.1:5000/api/buy"
TOTAL_REQUESTS = 20

def make_purchase(number):
    try:
        headers = {
            "Idempotency-Key": str(uuid.uuid4())
        }

        response = requests.post(
            URL,
            headers=headers,
            timeout=30
        )

        try:
            body = response.json()
        except ValueError:
            body = response.text

        return {
            "request": number,
            "status": response.status_code,
            "response": body
        }

    except Exception as error:
        return {
            "request": number,
            "status": "CONNECTION ERROR",
            "response": repr(error)
        }

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    results = list(
        executor.map(make_purchase, range(1, TOTAL_REQUESTS + 1))
    )

success = sum(1 for r in results if r["status"] == 201)
out_of_stock = sum(1 for r in results if r["status"] == 409)
errors = sum(
    1 for r in results
    if r["status"] not in (200, 201, 409)
)

for result in results:
    print(result)

print("\n----- TEST SUMMARY -----")
print("Total requests:", TOTAL_REQUESTS)
print("Successful orders:", success)
print("Out-of-stock responses:", out_of_stock)
print("Other errors:", errors)
