import json
import os
import asyncio
from google.antigravity import Agent, LocalAgentConfig, types
from google.antigravity.hooks import hooks

from classifier import classify_failure
from router import route_transaction

RETRIES_TRACKER = {}
TOTAL_RECOVERED = 0.0

@hooks.pre_tool_call_decide
async def limit_retries(data: types.ToolCall) -> types.HookResult:
    if data.name == "route_transaction":
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
    
def record_recovery(amount: float) -> str:
    """Records the successful recovery of a soft-decline transaction amount.
    
    Args:
        amount: The transaction amount recovered.
    """
    global TOTAL_RECOVERED
    TOTAL_RECOVERED += amount
    return f"Recorded ${amount:.2f} as recovered."

config = LocalAgentConfig(
    tools=[classify_failure, route_transaction, record_recovery],
    hooks=[limit_retries, audit_log]
)

async def main():
    async with Agent(config) as agent:
        with open(os.path.join(os.path.dirname(__file__), "synthetic_failures.json"), "r") as f:
            failures = json.load(f)
            
        # Process the first 10 for simulation
        for record in failures[:10]:
            tx_id = record["transaction_id"]
            amt = record["amount"]
            feat = record["features"]
            
            prompt = (
                f"Transaction {tx_id} of amount {amt} failed. Features: {feat}. "
                f"Use classify_failure to classify it. "
                f"If it's a soft decline, use route_transaction to route it. "
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
