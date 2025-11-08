#!/usr/bin/env python3
"""
FIX: Correct the 'const data = data.json;' error
This was created by the previous fix attempt. Should be 'const data = input.json;'
"""

import json
import sys

def fix_data_data_error(workflow):
    """Fix nodes with 'const data = data.json;' error"""
    print("=" * 80)
    print("FIXING 'const data = data.json' ERROR")
    print("=" * 80)

    nodes = workflow['nodes']
    fixed_count = 0

    for node in nodes:
        if node['type'] != 'n8n-nodes-base.code':
            continue

        code = node.get('parameters', {}).get('jsCode', '')

        # Check for the error pattern
        if 'const data = data.json;' in code:
            print(f"\n🔧 Fixing: {node['name']}")

            # Replace 'const data = data.json;' with 'const data = input.json;'
            fixed_code = code.replace('const data = data.json;', 'const data = input.json;')

            node['parameters']['jsCode'] = fixed_code
            fixed_count += 1
            print(f"   ✅ Changed 'const data = data.json;' → 'const data = input.json;'")

    return fixed_count

def main():
    print("🚀 Fixing data = data.json error\n")

    # Load workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow loaded: {len(workflow['nodes'])} nodes\n")
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

    # Fix the error
    fixed = fix_data_data_error(workflow)

    if fixed > 0:
        # Save workflow
        try:
            with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Workflow saved: {len(workflow['nodes'])} nodes")
        except Exception as e:
            print(f"\n❌ Error saving workflow: {e}")
            sys.exit(1)

    print("\n" + "=" * 80)
    print("FIX COMPLETED")
    print("=" * 80)
    print(f"\nNodes fixed: {fixed}")

    if fixed > 0:
        print("\n🎯 'const data = data.json' errors have been corrected!")
    else:
        print("\nℹ️  No errors found")

if __name__ == '__main__':
    main()
