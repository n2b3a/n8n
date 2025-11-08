#!/usr/bin/env python3
"""
FIX: Switch nodes missing outputsAmount parameter

In n8n Switch v3.3, you must specify how many outputs the node has
using parameters.options.outputsAmount

Without this, it defaults to 4 outputs (indexes 0-3)
"""

import json
import sys
import re

def fix_switch_node(node, connections):
    """Fix a Switch node to have correct outputsAmount"""
    name = node['name']
    params = node.get('parameters', {})

    # Count actual connections
    node_connections = connections.get(name, {}).get('main', [])
    actual_outputs = len(node_connections)

    print(f"\n🔧 Fixing: {name}")
    print(f"   Actual connections: {actual_outputs} outputs (0-{actual_outputs-1})")

    # Get current outputsAmount if it exists
    current_amount = params.get('options', {}).get('outputsAmount')

    if current_amount == actual_outputs:
        print(f"   ✅ Already correctly configured ({current_amount} outputs)")
        return False

    # Set outputsAmount
    if 'options' not in params:
        params['options'] = {}

    params['options']['outputsAmount'] = actual_outputs

    print(f"   ✅ Set outputsAmount: {actual_outputs}")

    # Verify the expression matches
    output_expr = params.get('output', '')

    # Find max output number in expression
    output_numbers = re.findall(r'\b(\d+)\b', output_expr)
    if output_numbers:
        max_output = max(int(n) for n in output_numbers)
        expected = max_output + 1

        if expected != actual_outputs:
            print(f"   ⚠️  WARNING: Expression uses max output {max_output} ({expected} outputs)")
            print(f"   ⚠️  But {actual_outputs} connections exist")
            print(f"   ⚠️  This may cause routing issues!")

    return True

def fix_all_switch_nodes(workflow):
    """Fix all Switch nodes in the workflow"""
    print("="*80)
    print("FIXING SWITCH NODE OUTPUT CONFIGURATIONS")
    print("="*80)

    nodes = workflow['nodes']
    connections = workflow['connections']

    switch_nodes = [n for n in nodes if n['type'] == 'n8n-nodes-base.switch']

    print(f"\nFound {len(switch_nodes)} Switch nodes\n")

    fixed_count = 0

    for node in switch_nodes:
        if fix_switch_node(node, connections):
            fixed_count += 1

    return fixed_count

def main():
    print("🚀 Fixing Switch node output configurations\n")

    # Load workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow loaded: {len(workflow['nodes'])} nodes\n")
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

    # Fix all Switch nodes
    fixed = fix_all_switch_nodes(workflow)

    if fixed > 0:
        # Save workflow
        try:
            with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Workflow saved: {len(workflow['nodes'])} nodes")
        except Exception as e:
            print(f"\n❌ Error saving workflow: {e}")
            sys.exit(1)

    print("\n" + "="*80)
    print("SWITCH NODE FIX COMPLETED")
    print("="*80)
    print(f"\nNodes fixed: {fixed}")

    if fixed > 0:
        print("\n🎯 All Switch nodes now have correct outputsAmount!")
        print("   This explicitly tells n8n how many outputs each Switch has")
    else:
        print("\nℹ️  All Switch nodes were already correctly configured")

if __name__ == '__main__':
    main()
