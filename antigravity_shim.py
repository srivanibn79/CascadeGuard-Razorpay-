import inspect
import re

class types:
    class ToolCall:
        def __init__(self, name, arguments):
            self.name = name
            self.arguments = arguments
            
    class HookResult:
        def __init__(self, allow=True, error_message=""):
            self.allow = allow
            self.error_message = error_message

class Hooks:
    def __init__(self):
        self.pre_decide = None
        self.on_end = None
        
    def pre_tool_call_decide(self, func):
        self.pre_decide = func
        return func
        
    def on_session_end(self, func):
        self.on_end = func
        return func

hooks = Hooks()

class LocalAgentConfig:
    def __init__(self, tools=None, hooks_list=None):
        self.tools = {t.__name__: t for t in (tools or [])}
        self.hooks_list = hooks_list or []

class Agent:
    def __init__(self, config):
        self.config = config
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if hooks.on_end:
            if inspect.iscoroutinefunction(hooks.on_end):
                await hooks.on_end()
            else:
                hooks.on_end()
                
    async def chat(self, prompt):
        async def _stream():
            # A lightweight fallback simulation of the LLM extracting arguments from the prompt
            tx_match = re.search(r"Transaction (\S+) of amount ([\d\.]+) failed at (\S+) with latency ([\d\.]+)s and error (\d+)", prompt)
            if not tx_match:
                yield "Invalid prompt format."
                return
                
            tx_id = tx_match.group(1)
            amt = float(tx_match.group(2))
            gateway = tx_match.group(3)
            lat = float(tx_match.group(4))
            code = int(tx_match.group(5))
            
            # 1. Execute Prediction Tool
            pred = self.config.tools["agent_predict"](lat, code)
            
            if pred == 1: # Soft decline
                # 2. Trigger Pre-Tool Decide Hook
                tc = types.ToolCall("agent_route", {"transaction_id": tx_id, "source_gateway": gateway})
                if hooks.pre_decide:
                    res = await hooks.pre_decide(tc) if inspect.iscoroutinefunction(hooks.pre_decide) else hooks.pre_decide(tc)
                    if not res.allow:
                        yield f"Tool execution denied by Decide Hook: {res.error_message}"
                        return
                        
                # 3. Execute Routing Tool
                dest = self.config.tools["agent_route"](tx_id, gateway)
                
                if dest != 'None' and len(dest) > 0:
                    self.config.tools["record_recovery"](amt)
                    yield f"Successfully re-routed via {dest} and recovered ${amt:.2f}."
                else:
                    yield "No valid route found."
            else:
                yield "Hard Fault - Dropped."
        
        return _stream()
