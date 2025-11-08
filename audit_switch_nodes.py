#!/usr/bin/env python3
"""
COMPREHENSIVE SWITCH NODE AUDIT

Analyze all Switch nodes to find mismatches between:
1. Output expression (how many outputs the code defines)
2. Actual connections (how many outputs are connected)
"""

import json
import sys
import re

def analyze_switch_node(node, connections, workflow_connections):
    """Analyze a single Switch node for errors"""
    name = node['name']
    params = node.get('parameters', {})
    output_expr = params.get('output', '')

    print(f"\n{'='*80}")
    print(f"ANALYZING: {name}")
    print('='*80)

    issues = []

    # Count outputs in expression
    # Ternary format: {{ condition ? 0 : condition2 ? 1 : condition3 ? 2 : 3 }}
    # Count the number of colons to determine outputs

    # Extract the expression content between {{ and }}
    match = re.search(r'\{\{(.+?)\}\}', output_expr)
    if match:
        expr = match.group(1)

        # Count question marks (number of conditions)
        question_marks = expr.count('?')

        # Find all output numbers in the expression
        output_numbers = re.findall(r'\b(\d+)\b', expr)
        output_numbers = [int(n) for n in output_numbers]

        if output_numbers:
            max_output = max(output_numbers)
            expected_outputs = max_output + 1

            print(f"\n📋 Output Expression Analysis:")
            print(f"   Expression: {output_expr[:100]}...")
            print(f"   Conditions: {question_marks}")
            print(f"   Output numbers found: {output_numbers}")
            print(f"   Max output index: {max_output}")
            print(f"   Expected total outputs: {expected_outputs}")
        else:
            print(f"\n⚠️  Could not parse output numbers from expression")
            expected_outputs = None
    else:
        print(f"\n⚠️  Could not parse expression: {output_expr}")
        expected_outputs = None

    # Count actual connections
    node_connections = workflow_connections.get(name, {}).get('main', [])
    actual_outputs = len([conn for conn in node_connections if conn])

    print(f"\n🔌 Actual Connections:")
    print(f"   Total outputs connected: {actual_outputs}")

    for i, conn_list in enumerate(node_connections):
        if conn_list:
            targets = [c['node'] for c in conn_list]
            print(f"   Output {i}: → {', '.join(targets)}")
        else:
            print(f"   Output {i}: (not connected)")

    # Check for mismatch
    if expected_outputs is not None:
        if actual_outputs < expected_outputs:
            issues.append({
                'severity': 'CRITICAL',
                'type': 'Missing connections',
                'message': f'Expression defines {expected_outputs} outputs but only {actual_outputs} are connected',
                'expected': expected_outputs,
                'actual': actual_outputs
            })
        elif actual_outputs > expected_outputs:
            issues.append({
                'severity': 'WARNING',
                'type': 'Extra connections',
                'message': f'Expression defines {expected_outputs} outputs but {actual_outputs} are connected',
                'expected': expected_outputs,
                'actual': actual_outputs
            })

    # Report issues
    if issues:
        print(f"\n❌ ISSUES FOUND:")
        for issue in issues:
            print(f"   [{issue['severity']}] {issue['type']}")
            print(f"   → {issue['message']}")
    else:
        print(f"\n✅ No issues found")

    return issues

def audit_all_switch_nodes(workflow):
    """Audit all Switch nodes in the workflow"""
    print("="*80)
    print("COMPREHENSIVE SWITCH NODE AUDIT")
    print("="*80)

    nodes = workflow['nodes']
    connections = workflow['connections']

    switch_nodes = [n for n in nodes if n['type'] == 'n8n-nodes-base.switch']

    print(f"\nFound {len(switch_nodes)} Switch nodes:")
    for node in switch_nodes:
        print(f"  - {node['name']}")

    all_issues = {}

    for node in switch_nodes:
        issues = analyze_switch_node(node, connections, connections)
        if issues:
            all_issues[node['name']] = issues

    return all_issues

def main():
    print("🚀 Starting comprehensive Switch node audit\n")

    # Load workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow loaded: {len(workflow['nodes'])} nodes\n")
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

    # Audit all Switch nodes
    issues = audit_all_switch_nodes(workflow)

    # Summary
    print("\n" + "="*80)
    print("AUDIT SUMMARY")
    print("="*80)

    if issues:
        print(f"\n❌ Found issues in {len(issues)} Switch node(s):\n")
        for node_name, node_issues in issues.items():
            print(f"  {node_name}:")
            for issue in node_issues:
                print(f"    [{issue['severity']}] {issue['message']}")
        print("\n⚠️  These nodes need to be fixed!")
        return 1
    else:
        print("\n✅ All Switch nodes are correctly configured!")
        return 0

if __name__ == '__main__':
    sys.exit(main())
