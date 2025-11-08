#!/usr/bin/env python3
"""
FIX: Duplicate 'input' variable declaration in Code nodes
When error handling wrapper was added, it creates 'const input = $input.first()'
If original code also has 'const input = ...', we get a conflict

Solution: Change the wrapper to use 'inputItem' instead of 'input' to avoid conflicts
"""

import json
import sys
import re

def fix_duplicate_input(workflow):
    """Fix Code nodes where 'input' variable is declared twice"""
    print("=" * 80)
    print("FIXING DUPLICATE INPUT VARIABLE DECLARATIONS")
    print("=" * 80)

    nodes = workflow['nodes']
    fixed_count = 0

    for node in nodes:
        if node['type'] != 'n8n-nodes-base.code':
            continue

        code = node.get('parameters', {}).get('jsCode', '')

        # Check if this has our error handling wrapper
        if '// ===== ERROR HANDLING & INPUT VALIDATION =====' not in code:
            continue

        # Check if there's a duplicate input declaration
        # Split by try block to separate wrapper from original code
        parts = code.split('// Original code starts here')
        if len(parts) != 2:
            continue

        wrapper_part = parts[0]
        original_part = parts[1]

        # Check if original part has 'const input = '
        if re.search(r'\bconst\s+input\s*=', original_part):
            print(f"\n🔧 Fixing: {node['name']}")

            # Strategy: Change the wrapper to use 'inputItem' instead of 'input'
            # This way the original code's 'input' variable won't conflict

            # In wrapper, replace: const input = $input.first();
            # With: const inputItem = $input.first();
            wrapper_part_fixed = wrapper_part.replace(
                'const input = $input.first();',
                'const inputItem = $input.first();'
            )

            # In wrapper, replace: if (!input || !input.json)
            # With: if (!inputItem || !inputItem.json)
            wrapper_part_fixed = wrapper_part_fixed.replace(
                'if (!input || !input.json)',
                'if (!inputItem || !inputItem.json)'
            )

            # In wrapper error returns, replace: input?.json?.phone_number
            # With: inputItem?.json?.phone_number
            wrapper_part_fixed = re.sub(
                r'\binput\?\.',
                'inputItem?.',
                wrapper_part_fixed
            )

            # Reconstruct the code
            fixed_code = wrapper_part_fixed + '// Original code starts here' + original_part

            node['parameters']['jsCode'] = fixed_code
            fixed_count += 1
            print(f"   ✅ Changed wrapper to use 'inputItem' instead of 'input'")
            print(f"   ✅ Original code's 'input' variable no longer conflicts")

    return fixed_count

def main():
    print("🚀 Fixing duplicate input variable declarations\n")

    # Load workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow loaded: {len(workflow['nodes'])} nodes\n")
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

    # Fix duplicate declarations
    fixed = fix_duplicate_input(workflow)

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
    print("DUPLICATE INPUT FIX COMPLETED")
    print("=" * 80)
    print(f"\nNodes fixed: {fixed}")

    if fixed > 0:
        print("\n🎯 Duplicate variable declarations have been resolved!")
        print("   Wrapper now uses 'inputItem' to avoid conflicts with original 'input' variable")
    else:
        print("\nℹ️  No duplicate declarations found")

if __name__ == '__main__':
    main()
