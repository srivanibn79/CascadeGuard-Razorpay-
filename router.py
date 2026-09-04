import collections

# A simple graph of payment gateways. 1 = healthy edge, 0 = unusable edge.
gateway_graph = {
    'Gateway_A': {'Gateway_B': 1, 'Gateway_C': 0},
    'Gateway_B': {'Gateway_D': 1, 'Gateway_A': 1},
    'Gateway_C': {'Gateway_E': 1, 'Gateway_A': 0},
    'Gateway_D': {'Gateway_B': 1},
    'Gateway_E': {'Gateway_C': 1},
}

# The state of the nodes: True if healthy, False if degraded.
gateway_health = {
    'Gateway_A': False,
    'Gateway_B': True,
    'Gateway_C': False,
    'Gateway_D': True,
    'Gateway_E': True,
}


def route_transaction(source_gateway: str):
    """Finds the shortest path (BFS) from source_gateway to the nearest healthy gateway.

    Args:
        source_gateway: The gateway where the transaction originally failed.

    Returns:
        A list of gateway names representing the path (including the source
        and the destination healthy gateway), or None if no healthy gateway
        is reachable.
    """
    if source_gateway not in gateway_graph:
        return None

    queue = collections.deque([[source_gateway]])
    visited = {source_gateway}

    while queue:
        path = queue.popleft()
        current_node = path[-1]

        if gateway_health.get(current_node):
            return path

        for neighbor, edge_weight in gateway_graph.get(current_node, {}).items():
            if neighbor not in visited and edge_weight == 1:
                visited.add(neighbor)
                queue.append(path + [neighbor])

    return None
