#!/usr/bin/env python3
"""
REVERT: Config Global references back to $('Config Global')

PROBLEM:
Changed references to $json.config.FIELD but this ONLY works if the node
receives data DIRECTLY from a flow that includes config.

Nodes like "Calcular % Preferencias" are in different branches and receive
data from other nodes (e.g., Supabase queries, AI agents) that don't have
'config' in their JSON.

SOLUTION:
Revert to using $('Config Global').first().json.FIELD
This works from ANY node because n8n allows referencing any previously
executed node, regardless of data flow path.
"""

import json
import sys
import re

def revert_config_references(workflow):
    """Revert Config Global references to use $('Config Global')"""
    print("=" * 80)
    print("REVERTING CONFIG GLOBAL REFERENCES")
    print("=" * 80)

    nodes = workflow['nodes']
    reverted_count = 0

    # Nodes that reference Config Global
    reference_nodes = [
        'Calcular % Preferencias',
        'Generar Menú Principal',
        'Validar Disponibilidad Precios',
        'Continuation Handler'
    ]

    for node in nodes:
        if node['name'] not in reference_nodes:
            continue

        if node['type'] != 'n8n-nodes-base.code':
            continue

        code = node.get('parameters', {}).get('jsCode', '')

        # Check if it has the problematic $json.config references
        if '$json.config.' not in code:
            continue

        print(f"\n🔧 Reverting: {node['name']}")

        # Replace all references:
        # $json.config.FIELD → $('Config Global').first().json.FIELD
        original_code = code

        # Pattern to match $json.config.FIELD_NAME
        pattern = r'\$json\.config\.(\w+)'
        replacement = r"$('Config Global').first().json.\1"

        updated_code = re.sub(pattern, replacement, code)

        if updated_code != original_code:
            node['parameters']['jsCode'] = updated_code
            reverted_count += 1

            # Show what was changed
            changes = re.findall(pattern, original_code)
            if changes:
                print(f"   ✅ Reverted {len(changes)} reference(s):")
                for field in set(changes):
                    print(f"      - $json.config.{field}")
                    print(f"        → $('Config Global').first().json.{field}")
        else:
            print(f"   ⚠️  No $json.config references found")

    return reverted_count

def verify_config_global_structure(workflow):
    """Verify Config Global returns correct structure"""
    print("\n" + "=" * 80)
    print("VERIFYING CONFIG GLOBAL STRUCTURE")
    print("=" * 80)

    nodes = workflow['nodes']

    # Find Config Global
    config_node = None
    for node in nodes:
        if node['name'] == 'Config Global':
            config_node = node
            break

    if not config_node:
        print("\n❌ Config Global not found!")
        return False

    code = config_node.get('parameters', {}).get('jsCode', '')

    print("\n📋 Config Global output structure:")

    if '...input' in code:
        print("   ✅ Preserves WhatsApp input data (...input)")
    else:
        print("   ⚠️  May not preserve input data")

    # Check what Config Global returns
    if 'config:' in code or 'config =' in code:
        print("   ✅ Adds 'config' property (nested)")
        print("\n   📝 Config Global returns:")
        print("      {")
        print("        ...whatsappData,  // messages, contacts, etc.")
        print("        config: { ... }   // config values")
        print("      }")
        print("\n   ✅ To access config from ANY node:")
        print("      $('Config Global').first().json.FIELD")
        print("\n   ❌ Do NOT use $json.config.FIELD")
        print("      (only works if config is in current node's JSON)")
    else:
        # Check if it returns flat structure
        if 'PRICE_VALIDITY_DAYS' in code or 'PREFERENCE_FIELDS_TOTAL' in code:
            print("   ✅ Returns config values directly")
            print("\n   ✅ To access config from ANY node:")
            print("      $('Config Global').first().json.FIELD")

    return True

def main():
    print("🚀 Reverting Config Global references\n")

    # Load workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow loaded: {len(workflow['nodes'])} nodes\n")
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

    # Revert references
    reverted = revert_config_references(workflow)

    # Verify structure
    verify_config_global_structure(workflow)

    if reverted > 0:
        # Save workflow
        try:
            with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Workflow saved: {len(workflow['nodes'])} nodes")
        except Exception as e:
            print(f"\n❌ Error saving workflow: {e}")
            sys.exit(1)

    print("\n" + "=" * 80)
    print("CONFIG REFERENCE REVERT COMPLETED")
    print("=" * 80)
    print(f"\nNodes reverted: {reverted}")

    if reverted > 0:
        print("\n🎯 All Config Global references reverted!")
        print("   Nodes now use: $('Config Global').first().json.FIELD")
        print("   This works from ANY node, ANY branch, ANY flow path")
    else:
        print("\nℹ️  No references needed reverting")

if __name__ == '__main__':
    main()
