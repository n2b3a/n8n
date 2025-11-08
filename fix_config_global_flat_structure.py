#!/usr/bin/env python3
"""
FIX: Config Global should return flat structure, not nested

PROBLEM:
Config Global returns: { ...input, config: {...} }
But references expect: $('Config Global').first().json.FIELD

SOLUTION:
Change Config Global to return: { ...input, ...config }
This puts config values at top level, making them accessible as:
$('Config Global').first().json.FIELD ✓
"""

import json
import sys

def fix_config_global_flat(workflow):
    """Fix Config Global to return flat structure"""
    print("=" * 80)
    print("FIXING CONFIG GLOBAL TO RETURN FLAT STRUCTURE")
    print("=" * 80)

    nodes = workflow['nodes']

    # Find Config Global
    for node in nodes:
        if node['name'] != 'Config Global':
            continue

        print("\n🔧 Updating Config Global code...")

        # Get current code
        code = node.get('parameters', {}).get('jsCode', '')

        # Replace: config: config
        # With: ...config
        new_code = code.replace(
            'config: config  // Add config as a nested object',
            '...config  // Add config values at top level'
        )

        # Also update the comment
        new_code = new_code.replace(
            '// Return original input WITH config added',
            '// Return original input WITH config values added at top level'
        )

        node['parameters']['jsCode'] = new_code

        print("✅ Config Global updated\n")
        print("📝 New return structure:")
        print("   return [{")
        print("     json: {")
        print("       ...input,    // WhatsApp data: messages, contacts, etc.")
        print("       ...config    // Config values: PRICE_VALIDITY_DAYS, etc.")
        print("     }")
        print("   }]")
        print("\n✅ Config values are now at TOP LEVEL")
        print("✅ Access as: $('Config Global').first().json.FIELD")

        return True

    print("❌ Config Global not found!")
    return False

def main():
    print("🚀 Fixing Config Global structure\n")

    # Load workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow loaded: {len(workflow['nodes'])} nodes\n")
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

    # Fix Config Global
    success = fix_config_global_flat(workflow)

    if not success:
        print("\n❌ Failed to fix Config Global")
        sys.exit(1)

    # Save workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Workflow saved: {len(workflow['nodes'])} nodes")
    except Exception as e:
        print(f"\n❌ Error saving workflow: {e}")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("CONFIG GLOBAL FIX COMPLETED")
    print("=" * 80)
    print("\n🎯 Config Global now returns FLAT structure")
    print("   ✅ WhatsApp data preserved")
    print("   ✅ Config values at top level")
    print("   ✅ Accessible from ANY node as:")
    print("      $('Config Global').first().json.FIELD_NAME")

if __name__ == '__main__':
    main()
