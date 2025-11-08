#!/usr/bin/env python3
"""
DEEP VALIDATION: Check for infinite loops, disconnected modules, and flow integrity
"""

import json
import sys
from collections import defaultdict, deque

def load_workflow():
    with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def build_graph(workflow):
    """Build directed graph of connections"""
    nodes = workflow['nodes']
    connections = workflow['connections']

    node_names = {node['name'] for node in nodes}

    # Build adjacency list
    graph = defaultdict(list)
    reverse_graph = defaultdict(list)

    for source_name, conn_data in connections.items():
        if 'main' in conn_data:
            for output_list in conn_data['main']:
                for conn in output_list:
                    target_name = conn['node']
                    graph[source_name].append(target_name)
                    reverse_graph[target_name].append(source_name)

    return graph, reverse_graph, node_names

def find_cycles(graph):
    """Detect cycles in directed graph using DFS"""
    cycles = []
    visited = set()
    rec_stack = set()
    path = []

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                # Found a cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)
                return True

        path.pop()
        rec_stack.remove(node)
        return False

    for node in graph.keys():
        if node not in visited:
            dfs(node)

    return cycles

def find_disconnected_nodes(workflow, graph, reverse_graph):
    """Find nodes that are not connected to the main flow"""
    nodes = workflow['nodes']
    node_names = {node['name'] for node in nodes}

    # Find trigger nodes (no incoming connections)
    trigger_nodes = []
    for node in nodes:
        name = node['name']
        if 'trigger' in node['type'].lower() or name not in reverse_graph:
            trigger_nodes.append(name)

    # BFS from trigger nodes to find all reachable nodes
    reachable = set()
    queue = deque(trigger_nodes)

    while queue:
        current = queue.popleft()
        if current in reachable:
            continue
        reachable.add(current)

        for neighbor in graph.get(current, []):
            if neighbor not in reachable:
                queue.append(neighbor)

    # Find disconnected nodes
    disconnected = node_names - reachable - set(trigger_nodes)

    return list(disconnected), trigger_nodes

def find_dead_ends(workflow, graph):
    """Find nodes that don't lead anywhere (potential dead ends)"""
    nodes = workflow['nodes']

    dead_ends = []
    for node in nodes:
        name = node['name']
        node_type = node['type']

        # Skip nodes that are expected to be endpoints
        if any(keyword in name.lower() for keyword in ['enviar', 'send', 'respuesta', 'error handler']):
            continue

        # Skip certain node types that are expected to be endpoints
        if node_type in ['n8n-nodes-base.whatsApp', 'n8n-nodes-base.supabase']:
            continue

        # Check if node has no outgoing connections
        if name not in graph or len(graph[name]) == 0:
            dead_ends.append({
                'name': name,
                'type': node_type
            })

    return dead_ends

def check_switch_nodes(workflow, graph):
    """Verify Switch nodes have all outputs connected"""
    nodes = workflow['nodes']
    issues = []

    for node in nodes:
        if node['type'] == 'n8n-nodes-base.switch':
            name = node['name']

            # Get the output expression
            parameters = node.get('parameters', {})
            output_expr = parameters.get('output', '')

            # Count expected outputs (count ternary operators + 1)
            # Format: {{ condition ? 0 : condition2 ? 1 : 2 }}
            ternary_count = output_expr.count('?')
            expected_outputs = ternary_count + 1 if ternary_count > 0 else 2

            # Get actual connections
            connections = workflow['connections'].get(name, {}).get('main', [])
            actual_outputs = len([conn for conn in connections if conn])

            if actual_outputs < expected_outputs:
                issues.append({
                    'node': name,
                    'expected': expected_outputs,
                    'actual': actual_outputs,
                    'missing': expected_outputs - actual_outputs
                })

    return issues

def analyze_continuation_flow(workflow, graph):
    """Specifically analyze the continuation flow for issues"""
    nodes = workflow['nodes']
    node_names = {node['name'] for node in nodes}

    # Key nodes in continuation flow
    continuation_nodes = [
        'Continuation Handler',
        'Update Session DB',
        'Enviar Respuesta',
        'Router Continuação',
        'Detectar Opção Continuação'
    ]

    issues = []
    for node_name in continuation_nodes:
        if node_name not in node_names:
            issues.append(f"Missing: {node_name}")
        elif node_name not in graph:
            issues.append(f"No outgoing connections: {node_name}")

    return issues

def main():
    print("=" * 80)
    print("DEEP VALIDATION - CHECKING FOR LOOPS, DISCONNECTED NODES, AND FLOW ISSUES")
    print("=" * 80)

    workflow = load_workflow()
    graph, reverse_graph, node_names = build_graph(workflow)

    print(f"\n📊 Workflow Stats:")
    print(f"   Total nodes: {len(node_names)}")
    print(f"   Total connections: {sum(len(v) for v in graph.values())}")

    # 1. Check for infinite loops
    print("\n" + "=" * 80)
    print("1. CHECKING FOR INFINITE LOOPS")
    print("=" * 80)

    cycles = find_cycles(graph)
    if cycles:
        print(f"\n❌ Found {len(cycles)} cycle(s):")
        for i, cycle in enumerate(cycles, 1):
            print(f"\n   Cycle {i}:")
            for node in cycle:
                print(f"      → {node}")
        print("\n⚠️  WARNING: Infinite loops detected! Workflow may hang.")
    else:
        print("\n✅ No infinite loops detected")

    # 2. Check for disconnected modules
    print("\n" + "=" * 80)
    print("2. CHECKING FOR DISCONNECTED MODULES")
    print("=" * 80)

    disconnected, triggers = find_disconnected_nodes(workflow, graph, reverse_graph)

    print(f"\n📍 Trigger nodes found: {len(triggers)}")
    for trigger in triggers:
        print(f"   - {trigger}")

    if disconnected:
        print(f"\n❌ Found {len(disconnected)} disconnected node(s):")
        for node in disconnected:
            print(f"   - {node}")
        print("\n⚠️  WARNING: Some nodes are not reachable from triggers!")
    else:
        print("\n✅ All nodes are connected to the main flow")

    # 3. Check for dead ends
    print("\n" + "=" * 80)
    print("3. CHECKING FOR UNEXPECTED DEAD ENDS")
    print("=" * 80)

    dead_ends = find_dead_ends(workflow, graph)
    if dead_ends:
        print(f"\n⚠️  Found {len(dead_ends)} potential dead end(s):")
        for de in dead_ends:
            print(f"   - {de['name']} ({de['type']})")
        print("\n   Note: These nodes have no outgoing connections.")
        print("   This may be intentional for some nodes.")
    else:
        print("\n✅ No unexpected dead ends found")

    # 4. Check Switch node connections
    print("\n" + "=" * 80)
    print("4. CHECKING SWITCH NODE OUTPUTS")
    print("=" * 80)

    switch_issues = check_switch_nodes(workflow, graph)
    if switch_issues:
        print(f"\n❌ Found {len(switch_issues)} Switch node(s) with missing outputs:")
        for issue in switch_issues:
            print(f"   - {issue['node']}: Expected {issue['expected']} outputs, got {issue['actual']}")
        print("\n⚠️  WARNING: Switch nodes should have all outputs connected!")
    else:
        print("\n✅ All Switch nodes have proper output connections")

    # 5. Check continuation flow
    print("\n" + "=" * 80)
    print("5. CHECKING CONTINUATION FLOW INTEGRITY")
    print("=" * 80)

    continuation_issues = analyze_continuation_flow(workflow, graph)
    if continuation_issues:
        print(f"\n❌ Found {len(continuation_issues)} issue(s) in continuation flow:")
        for issue in continuation_issues:
            print(f"   - {issue}")
    else:
        print("\n✅ Continuation flow is properly connected")

    # Final verdict
    print("\n" + "=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)

    total_issues = len(cycles) + len(disconnected) + len(switch_issues) + len(continuation_issues)

    if total_issues == 0:
        print("\n🎉 PERFECT! Workflow is ready to import:")
        print("   ✅ No infinite loops")
        print("   ✅ All nodes connected")
        print("   ✅ All Switch outputs connected")
        print("   ✅ Continuation flow intact")
        print("   ✅ No blocking issues")
        print("\n✨ You can import this workflow to n8n right now!")
        return 0
    else:
        print(f"\n⚠️  Found {total_issues} issue(s) that need attention:")
        if cycles:
            print(f"   ❌ {len(cycles)} infinite loop(s)")
        if disconnected:
            print(f"   ❌ {len(disconnected)} disconnected node(s)")
        if switch_issues:
            print(f"   ❌ {len(switch_issues)} Switch node(s) with missing outputs")
        if continuation_issues:
            print(f"   ❌ {len(continuation_issues)} continuation flow issue(s)")
        return 1

if __name__ == '__main__':
    sys.exit(main())
