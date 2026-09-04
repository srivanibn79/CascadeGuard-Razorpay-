import json
import os
# pyrefly: ignore [missing-import]
import torch
import random

from data_generator import generate_data
from classifier import train_model, predict
from router import route_transaction

def run_verification():
    torch.manual_seed(42)
    random.seed(42)
    
    print("--- 1. Generating Synthetic Dataset ---")
    generate_data()
    file_path = os.path.join(os.path.dirname(__file__), "synthetic_failures.json")
    
    with open(file_path, "r") as f:
        data = json.load(f)
        
    print(f"Dataset generated with {len(data)} records.")
    
    print("\n--- 2. Training PyTorch Model ---")
    model = train_model(data, epochs=100, lr=0.05)
    
    print("\n--- 3. Running Compliance, Predictions & Routing (BFS) ---")
    
    audit_trail = []
    escalation_queue = []
    
    hard_faults_rejected = 0
    soft_declines_found = 0
    successful_reroutes = 0
    recovered_revenue = 0.0
    
    for record in data:
        prediction = predict(model, record["latency_sec"], record["error_code"])
        tx_id = record["transaction_id"]
        
        if prediction == 1: # Soft Decline
            soft_declines_found += 1
            path = route_transaction(record["source_gateway"])
            
            if path:
                hops = len(path) - 1
                if hops <= 3:
                    successful_reroutes += 1
                    recovered_revenue += record["amount"]
                    audit_trail.append({"transaction_id": tx_id, "status": "RECOVERED", "hops": hops})
                else:
                    audit_trail.append({"transaction_id": tx_id, "status": "FAILED"})
                    escalation_queue.append({"transaction_id": tx_id, "reason": "Max Retries Exceeded / No Route"})
            else:
                audit_trail.append({"transaction_id": tx_id, "status": "FAILED"})
                escalation_queue.append({"transaction_id": tx_id, "reason": "Max Retries Exceeded / No Route"})
        else:
            hard_faults_rejected += 1
            audit_trail.append({"transaction_id": tx_id, "status": "REJECTED"})
            escalation_queue.append({"transaction_id": tx_id, "reason": "Hard Fault - Compliance Review"})
            
    print(f"\n--- 4. Saving Audit Trails ---")
    with open(os.path.join(os.path.dirname(__file__), "audit_log.json"), "w") as f:
        json.dump(audit_trail, f, indent=4)
        
    with open(os.path.join(os.path.dirname(__file__), "escalation_queue.json"), "w") as f:
        json.dump(escalation_queue, f, indent=4)
        
    print("Generated audit_log.json and escalation_queue.json.")
        
    print(f"\n--- 5. Final Recovery Summary ---")
    print(f"Total Records: {len(data)}")
    print(f"Hard Faults Rejected: {hard_faults_rejected}")
    print(f"Soft Declines Identified: {soft_declines_found}")
    print(f"Successful Re-routings: {successful_reroutes}")
    print(f"Total Value Recovered: ${recovered_revenue:,.2f}")

if __name__ == "__main__":
    run_verification()
