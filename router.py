import collections

# A simple graph of payment gateways
# 1 is healthy, 0 is invalid/degraded
gateway_graph = {
    'Gateway_A': {'Gateway_B': 1, 'Gateway_C': 0},
    'Gateway_B': {'Gateway_D': 1},
    'Gateway_C': {'Gateway_E': 1},
    'Gateway_D': {},
    'Gateway_E': {}
}

# The state of the nodes: True if healthy, False if degraded
gateway_health = {
    'Gateway_A': False,
    'Gateway_B': True,
    'Gateway_C': False,
    'Gateway_D': True,
    'Gateway_E': True
}

def route_transaction(transaction_id: str) -> str:
    """Routes the failed 'soft decline' transaction to a healthy node using BFS.
    
    Args:
        transaction_id: The ID of the transaction to route.
        
    Returns:
        The name of the healthy gateway, or 'None' if routing fails.
    """
    queue = collections.deque(['Gateway_A'])
    visited = set(['Gateway_A'])
    
    while queue:
        current_node = queue.popleft()
        
        if gateway_health.get(current_node):
            return current_node
            
        for neighbor, edge_weight in gateway_graph.get(current_node, {}).items():
            if neighbor not in visited and edge_weight == 1:
                visited.add(neighbor)
                queue.append(neighbor)
                
    return 'None'
