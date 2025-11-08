#!/usr/bin/env python3
"""
FIX: Continuation Handler self-loop
The node should connect to 'Update Session DB', not to itself
"""

import json
import sys

def fix_selfloop(workflow):
    """Fix Continuation Handler self-loop"""
    print("=" * 80)
    print("FIXING CONTINUATION HANDLER SELF-LOOP")
    print("=" * 80)

    connections = workflow['connections']

    # Check current connection
    current_conn = connections.get('Continuation Handler', {})
    print(f"\nCurrent connection:")
    print(f"  Continuation Handler → {current_conn.get('main', [[]])[0][0]['node'] if current_conn.get('main') and current_conn['main'][0] else 'None'}")

    # Fix the connection
    connections['Continuation Handler'] = {
        "main": [[{
            "node": "Update Session DB",
            "type": "main",
            "index": 0
        }]]
    }

    print(f"\n✅ Fixed connection:")
    print(f"  Continuation Handler → Update Session DB")

    return True

def main():
    print("🚀 Fixing Continuation Handler self-loop\n")

    # Load workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow loaded: {len(workflow['nodes'])} nodes\n")
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

    # Fix self-loop
    fix_selfloop(workflow)

    # Save workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Workflow saved: {len(workflow['nodes'])} nodes")
    except Exception as e:
        print(f"\n❌ Error saving workflow: {e}")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("SELF-LOOP FIX COMPLETED")
    print("=" * 80)
    print("\n🎯 Continuation Handler now properly connects to Update Session DB")

if __name__ == '__main__':
    main()
