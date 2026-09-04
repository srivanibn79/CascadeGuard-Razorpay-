import json
import os
import asyncio

try:
    # pyrefly: ignore [missing-import]
    from google.antigravity import Agent, LocalAgentConfig, types
    # pyrefly: ignore [missing-import]
    from google.antigravity.hooks import hooks
except ImportError:
    from antigravity_shim import Agent, LocalAgentConfig, types, hooks

from classifier import FailureClassifier, train_model, predict
from router import route_transaction

RETRIES_TRACKER = {}
TOTAL_RECOVERED = 0.0
AGENT_AUDIT = []

@hooks.pre_tool_call_decide
async def limit_retries(data: types.ToolCall) -> types.HookResult:
    if data.name == "agent_route":
        args = data.arguments
        tx_id = args.get("transaction_id", "default")
        
        retries = RETRIES_TRACKER.get(tx_id, 0)
        if retries >= 3:
            return types.HookResult(allow=False, error_message="Max retries reached")
            
        RETRIES_TRACKER[tx_id] = retries + 1
        
    return types.HookResult(allow=True)

@hooks.on_session_end
async def audit_log():
    print(f"--- FINAL AUDIT LOG ---")
    print(f"Total revenue recovered from successful soft-decline re-routings: ${TOTAL_RECOVERED:.2f}")
    with open(os.path.join(os.path.dirname(__file__), "agent_audit_log.json"), "w") as f:
        json.dump({"total_recovered": TOTAL_RECOVERED, "audit_events": AGENT_AUDIT}, f, indent=4)

def record_recovery(amount: float) -> str:
    """Records the successful recovery of a soft-decline transaction amount.
    
    Args:
        amount: The transaction amount recovered.
    """
    global TOTAL_RECOVERED, AGENT_AUDIT
    TOTAL_RECOVERED += amount
    AGENT_AUDIT.append({"status": "RECOVERED", "amount": amount})
    return f"Recorded ${amount:.2f} as recovered."

# Load Data & Train Model Once
with open(os.path.join(os.path.dirname(__file__), "synthetic_failures.json"), "r") as f:
    failures = json.load(f)

print("Training PyTorch model...")
trained_model = train_model(failures, epochs=100, lr=0.05)

def agent_predict(latency_sec: float, error_code: int) -> int:
    """Classifies the transaction failure using the trained PyTorch model.
    Returns 1 for Soft Decline and 0 for Hard Fault.
    """
    return predict(trained_model, latency_sec, error_code)

def agent_route(transaction_id: str, source_gateway: str) -> str:
    """Routes the transaction starting from the source_gateway using BFS.
    """
    path = route_transaction(source_gateway)
    if path:
        return path[-1]
    return 'None'

config = LocalAgentConfig(
    tools=[agent_predict, agent_route, record_recovery],
    hooks_list=[limit_retries, audit_log]
)

async def main():
    async with Agent(config) as agent:
        # Process the first 10 for simulation
        for record in failures[:10]:
            tx_id = record["transaction_id"]
            amt = record["amount"]
            lat = record["latency_sec"]
            code = record["error_code"]
            gateway = record["source_gateway"]
            
            prompt = (
                f"Transaction {tx_id} of amount {amt} failed at {gateway} with latency {lat}s and error {code}. "
                f"Use agent_predict to classify it. "
                f"If it's a soft decline (returns 1), use agent_route to route it from {gateway} (pass {tx_id} as transaction_id). "
                f"If routed successfully (i.e. router returns a healthy gateway), use record_recovery to record the {amt}."
            )
            print(f"Processing TX: {tx_id}")
            response = await agent.chat(prompt)
            async for chunk in response:
                pass
            print(f"TX {tx_id} processed.")

if __name__ == "__main__":
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "synthetic_failures.json")):
        import data_generator
        data_generator.generate_data()
        
    asyncio.run(main())
