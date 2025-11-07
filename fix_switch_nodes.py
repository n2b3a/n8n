#!/usr/bin/env python3
"""
Fix Switch nodes to use consistent structure with expression mode
"""

import json

def main():
    print("🔧 Fixing Switch node structure...\n")

    with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    print(f"✅ Loaded workflow with {len(workflow['nodes'])} nodes\n")

    # Find and fix the problematic Switch node
    for node in workflow['nodes']:
        if node['name'] == 'Router: ¿Es Decisión Duplicado?':
            print(f"Found problematic node: {node['name']}")
            print(f"  Current typeVersion: {node.get('typeVersion')}")
            print(f"  Current parameters: {list(node['parameters'].keys())}")

            # Update to match other Switch nodes in the workflow
            node['typeVersion'] = 3.3
            node['parameters'] = {
                "mode": "expression",
                "output": "=Output (0): {{ $json.is_duplicate_decision === true }}\nOutput (1): {{ $json.is_duplicate_decision === false || $json.is_duplicate_decision === undefined }}"
            }

            print(f"  ✅ Updated to typeVersion: 3.3")
            print(f"  ✅ Changed to expression mode")
            print()

    # Remove empty "options": {} from all nodes where it's not needed
    print("🧹 Removing unnecessary empty options...")
    removed_count = 0

    for node in workflow['nodes']:
        params = node.get('parameters', {})

        # Only remove empty options from nodes we added
        if 'options' in params and params['options'] == {}:
            node_id = node.get('id', '')
            # Check if this is one of our new nodes
            if any(new_id in node_id for new_id in [
                'ROUTER_DUPLICATE_DECISION',
                'CHECK_IF_DUPLICATE',
                'HANDLE_DUPLICATE_SUPPLIER_DECISION',
                'DETECT_DUPLICATE_DECISION'
            ]):
                del params['options']
                print(f"  Removed empty options from: {node['name']}")
                removed_count += 1

    print(f"  ✅ Removed {removed_count} empty options\n")

    # Save fixed workflow
    with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

    print("✅ Saved fixed workflow")
    print("\n✨ Workflow should now import correctly!")

if __name__ == '__main__':
    main()
