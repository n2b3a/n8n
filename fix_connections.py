#!/usr/bin/env python3
"""
Fix n8n workflow connections to use node names instead of IDs
"""

import json

def main():
    print("🔧 Fixing n8n workflow connections...\n")

    # Load workflow
    with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    print(f"✅ Loaded workflow with {len(workflow['nodes'])} nodes\n")

    # Create mapping of ID to Name
    id_to_name = {}
    name_to_id = {}

    for node in workflow['nodes']:
        node_id = node.get('id')
        node_name = node.get('name')
        id_to_name[node_id] = node_name
        name_to_id[node_name] = node_id

    print("📋 ID to Name mapping:")
    print("-" * 80)

    # Show mappings for our new/modified nodes
    important_ids = [
        'GENERATE_MAIN_MENU',
        'GENERATE_PREFERENCES_SUBMENU',
        'DETECT_PREFERENCE_OPTION',
        'ROUTER_PREFERENCES',
        'AGENT_CONFIG_PRODUTOS',
        'AGENT_REGISTER_FORNECEDOR',
        'DETECT_FORNECEDOR_COMPLETE',
        'IF_FORNECEDOR_COMPLETE',
        'SAVE_FORNECEDOR_DB',
        'HANDLE_DUPLICATE_SUPPLIER_DECISION',
        'CHECK_IF_DUPLICATE',
        'DETECT_DUPLICATE_DECISION',
        'ROUTER_DUPLICATE_DECISION'
    ]

    for node_id in important_ids:
        if node_id in id_to_name:
            print(f"  {node_id:40} → {id_to_name[node_id]}")

    print()

    # Fix connections
    print("🔄 Fixing connections...")
    fixed_connections = {}
    fixes_made = 0

    for source, conn_data in workflow.get('connections', {}).items():
        # Check if source is an ID instead of name
        if source in id_to_name and source != id_to_name[source]:
            # Source is an ID, convert to name
            actual_source = id_to_name[source]
            print(f"  ⚠️  Source: '{source}' → '{actual_source}'")
            fixes_made += 1
        else:
            actual_source = source

        # Fix target connections
        fixed_conn_data = {}

        for conn_type, conn_list in conn_data.items():
            fixed_conn_list = []

            for conn_group in conn_list:
                fixed_conn_group = []

                for conn in conn_group:
                    target = conn.get('node')

                    # Check if target is an ID instead of name
                    if target in id_to_name and target != id_to_name[target]:
                        actual_target = id_to_name[target]
                        print(f"  ⚠️  Target: '{target}' → '{actual_target}'")
                        fixes_made += 1

                        fixed_conn = conn.copy()
                        fixed_conn['node'] = actual_target
                        fixed_conn_group.append(fixed_conn)
                    else:
                        fixed_conn_group.append(conn)

                fixed_conn_list.append(fixed_conn_group)

            fixed_conn_data[conn_type] = fixed_conn_list

        fixed_connections[actual_source] = fixed_conn_data

    workflow['connections'] = fixed_connections

    print(f"\n✅ Made {fixes_made} fixes to connections\n")

    # Save fixed workflow
    with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

    print("✅ Saved fixed workflow")
    print("\n🔍 Running validation...")

    # Re-validate
    from validate_workflow import validate_connections

    conn_issues = validate_connections(workflow)

    if conn_issues:
        print("\n⚠️  Remaining issues:")
        for issue in conn_issues:
            print(f"  - {issue}")
    else:
        print("\n✅ All connections now valid!")

    print("\n✨ Workflow should now import correctly into n8n")

if __name__ == '__main__':
    main()
