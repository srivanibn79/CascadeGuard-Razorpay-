# CascadeGuard

**Submission for Razorpay AI Buildathon 2026 — Track 03: AI Revenue Recovery**

## Executive Summary

Traditional payment retries rely on static, linear schedules which burn gateway fees and trigger false-positive fraud locks by repeatedly hitting degraded nodes or repeating hard-declined transactions. CascadeGuard reimagines this process by dynamically classifying failures and intelligently routing soft declines around degraded infrastructure. This approach minimizes costs while maximizing successful revenue recovery.

## System Architecture

CascadeGuard utilizes a streamlined pipeline for intelligent payment routing:

```text
+-------------------------------------------------------------+
| 1. Synthetic Failure Ingestion                              |
|    (100 Test Transaction Batch)                             |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| 2. PyTorch Failure Classifier                               |
|    - Hard Faults (Dropped)                                  |
|    - Soft Declines (Routed)                                 |
+------------------------------+------------------------------+
                               | Soft Declines
                               v
+-------------------------------------------------------------+
| 3. BFS Dynamic Router                                       |
|    Graph node navigation & degraded node bypass             |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| 4. Antigravity Bounded Agent                                |
|    - Decide Hook (Max 3 Retries)                            |
|    - Inspect Hook (Audit Logs)                              |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| 5. Final Output Metric                                      |
|    Verified Recovered Revenue: $34,967.72                   |
+-------------------------------------------------------------+
```

## Repository Structure & File Usage

| File Name | Purpose |
| :--- | :--- |
| `data_generator.py` | Generates 100 synthetic transaction failures (latency, error codes, amounts) for testing. |
| `classifier.py` | PyTorch neural network that classifies failures as recoverable soft declines (1) or hard faults (0). |
| `router.py` | Implements BFS pathfinding across a simulated gateway graph to find healthy routing detours. |
| `agent.py` | The main orchestration layer. Chains tools together and enforces retry limits and audit hooks. |
| `verify_modules.py` | End-to-end mathematical verification harness proving 100% accuracy and bounding logic. |
| `antigravity_shim.py` | Local compatibility wrapper mimicking the Antigravity SDK to allow local execution of hooks. |
| `audit_log.json` | Persistent receipt of all successfully recovered transactions and their hop counts. |
| `escalation_queue.json` | Persistent log of hard faults and failed retries flagged for human compliance review. |
| `requirements.txt` | Defines standard Python dependencies required to run the pipeline. |

## Verified Test Run & Reproducibility

To ensure identical recovery metrics across all environments, all random operations and PyTorch initializations are locked with `seed(42)`. The PyTorch classifier achieved **100.00% Training Accuracy** on the synthetic dataset.

Below is the verified deterministic output from executing the end-to-end pipeline:

```text
--- 1. Generating Synthetic Dataset ---
Dataset generated with 100 records.

--- 2. Training PyTorch Model ---
Training completed. Final Training Accuracy: 100.00%

--- 3. Running Compliance, Predictions & Routing (BFS) ---

--- 4. Saving Audit Trails ---
Generated audit_log.json and escalation_queue.json.

--- 5. Final Recovery Summary ---
Total Records: 100
Hard Faults Rejected: 28
Soft Declines Identified: 72
Successful Re-routings: 72
Total Value Recovered: $34,967.72
```

## Fintech Compliance

To guarantee rigorous financial safety, the system natively enforces a **strict 3-hop limit** on any re-routing path. Transactions exceeding this limit are immediately dropped to prevent runaway execution. The platform actively generates two persistent logs for complete compliance tracking:
- **`audit_log.json`**: A strict ledger recording all successfully recovered transactions alongside their exact routing hop counts.
- **`escalation_queue.json`**: A secondary queue that flags Hard Faults (requiring Compliance Review) and retry-exceeded soft declines, ensuring no failed transaction goes unmonitored.

## Limitations & Next Steps

- **Dynamic Fee Modeling**: Future iterations could incorporate real-time gateway interchange fees into BFS edge weights, allowing for cost-weighted Dijkstra routing.
- **Continuous Drift Detection**: Implementing online learning to detect shifting bank decline distributions over time.
- **Compatibility Shim Disclosure**: An in-tree compatibility shim (`antigravity_shim.py`) is provided to demonstrate the Antigravity Agent hook lifecycle natively and locally, bypassing third-party container lock-in.
