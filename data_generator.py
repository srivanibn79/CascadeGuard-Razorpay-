import json
import random
import uuid
import os

def generate_data():
    records = []
    for _ in range(100):
        records.append({
            "transaction_id": str(uuid.uuid4()),
            "amount": round(random.uniform(10.0, 1000.0), 2),
            "features": [random.uniform(0, 1), random.uniform(0, 1)]
        })
    
    file_path = os.path.join(os.path.dirname(__file__), "synthetic_failures.json")
    with open(file_path, "w") as f:
        json.dump(records, f, indent=4)
        
if __name__ == "__main__":
    generate_data()
