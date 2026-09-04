import json
import random
import uuid
import os

GATEWAYS = ['Gateway_A', 'Gateway_B', 'Gateway_C', 'Gateway_D', 'Gateway_E']
ERROR_CODES = [200, 400, 402, 502, 504]

def generate_data():
    records = []
    for _ in range(100):
        records.append({
            "transaction_id": str(uuid.uuid4()),
            "amount": round(random.uniform(10.0, 1000.0), 2),
            "latency_sec": round(random.uniform(0.1, 5.0), 2),
            "error_code": random.choice(ERROR_CODES),
            "source_gateway": random.choice(GATEWAYS),
        })

    file_path = os.path.join(os.path.dirname(__file__), "synthetic_failures.json")
    with open(file_path, "w") as f:
        json.dump(records, f, indent=4)

if __name__ == "__main__":
    generate_data()
