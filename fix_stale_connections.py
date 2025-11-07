#!/usr/bin/env python3
"""
FIX: Clean up stale connection references
After Sprint 3 Fix #6, some connections still reference removed nodes
"""

import json
import sys

def fix_stale_connections(workflow):
    """Fix connections that reference nodes that no longer exist"""
    print("=" * 80)
    print("FIXING STALE CONNECTION REFERENCES")
    print("=" * 80)

    connections = workflow['connections']
    nodes = workflow['nodes']
    node_names = {node['name'] for node in nodes}

    print(f"\n📍 Total nodes in workflow: {len(nodes)}")
    print(f"📍 Total connection sources: {len(connections)}\n")

    # Find stale connection sources
    stale_sources = []
    for source_name in list(connections.keys()):
        if source_name not in node_names:
            stale_sources.append(source_name)
            print(f"⚠️  Found stale connection source: '{source_name}'")

    if not stale_sources:
        print("✅ No stale connections found!")
        return 0

    # Fix each stale connection
    fixed_count = 0
    for stale_source in stale_sources:
        print(f"\n🔧 Fixing: {stale_source}")

        # Check if this is the known "Marcar Sessão Completa" → "Continuation Handler" rename
        if stale_source == 'Marcar Sessão Completa':
            # This was replaced by "Continuation Handler" in Sprint 3 Fix #6
            # But actually, looking at the code, we might have removed it entirely
            # Let me check what connections it has

            conn_data = connections[stale_source]
            print(f"  Connection data: {conn_data}")

            # Check if "Continuation Handler" exists
            if "Continuation Handler" in node_names:
                print(f"  → Renaming connection to 'Continuation Handler'")
                connections['Continuation Handler'] = connections.pop(stale_source)
                fixed_count += 1
                print(f"  ✅ Connection renamed")
            else:
                # Remove the stale connection entirely
                print(f"  → Removing stale connection (no replacement found)")
                del connections[stale_source]
                fixed_count += 1
                print(f"  ✅ Connection removed")
        else:
            # Generic case: just remove the stale connection
            print(f"  → Removing stale connection")
            del connections[stale_source]
            fixed_count += 1
            print(f"  ✅ Connection removed")

    return fixed_count

def verify_all_connections(workflow):
    """Verify all connections reference existing nodes"""
    print("\n" + "=" * 80)
    print("VERIFYING ALL CONNECTIONS")
    print("=" * 80)

    nodes = workflow['nodes']
    connections = workflow['connections']
    node_names = {node['name'] for node in nodes}

    issues = []

    # Check all connection sources exist
    for source_name in connections.keys():
        if source_name not in node_names:
            issues.append(f"Source '{source_name}' not found in nodes")

    # Check all connection targets exist
    for source_name, conn_data in connections.items():
        if 'main' in conn_data:
            for output_index, output_list in enumerate(conn_data['main']):
                for conn in output_list:
                    target_name = conn['node']
                    if target_name not in node_names:
                        issues.append(f"Target '{target_name}' (from {source_name}) not found in nodes")

    if issues:
        print(f"\n❌ Found {len(issues)} connection issues:\n")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("\n✅ All connections verified - no issues found!")
        return True

def main():
    print("🚀 Cleaning up stale connections\n")

    # Load workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow loaded: {len(workflow['nodes'])} nodes\n")
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

    # Fix stale connections
    fixed = fix_stale_connections(workflow)

    # Verify all connections are now valid
    all_valid = verify_all_connections(workflow)

    # Save workflow
    if fixed > 0:
        try:
            with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Workflow saved: {len(workflow['nodes'])} nodes")
        except Exception as e:
            print(f"\n❌ Error saving workflow: {e}")
            sys.exit(1)
    else:
        print("\nℹ️  No changes made - workflow not saved")

    print("\n" + "=" * 80)
    print("STALE CONNECTION CLEANUP COMPLETED")
    print("=" * 80)
    print(f"\nConnections fixed: {fixed}")
    print(f"Validation status: {'✅ PASS' if all_valid else '❌ FAIL'}")

    if all_valid:
        print("\n🎯 Workflow is now ready for import to n8n!")
    else:
        print("\n⚠️  Additional issues found - see details above")
        sys.exit(1)

if __name__ == '__main__':
    main()
