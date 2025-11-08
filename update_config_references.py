#!/usr/bin/env python3
"""
Update nodes that reference Config Global to use new structure

OLD: $('Config Global').first().json.FIELD_NAME
NEW: $json.config.FIELD_NAME

This works because Config Global is now in the flow and adds
config values to the data stream.
"""

import json
import sys
import re

def update_config_references(workflow):
    """Update all references to Config Global"""
    print("=" * 80)
    print("UPDATING CONFIG GLOBAL REFERENCES")
    print("=" * 80)

    nodes = workflow['nodes']
    updated_count = 0

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

        # Check if it references Config Global
        if "$('Config Global')" not in code:
            continue

        print(f"\n🔧 Updating: {node['name']}")

        # Replace all references:
        # $('Config Global').first().json.FIELD → $json.config.FIELD
        original_code = code

        # Pattern to match $('Config Global').first().json.FIELD_NAME
        pattern = r"\$\('Config Global'\)\.first\(\)\.json\.(\w+)"
        replacement = r"$json.config.\1"

        updated_code = re.sub(pattern, replacement, code)

        if updated_code != original_code:
            node['parameters']['jsCode'] = updated_code
            updated_count += 1

            # Show what was changed
            changes = re.findall(pattern, original_code)
            if changes:
                print(f"   ✅ Updated {len(changes)} reference(s):")
                for field in set(changes):
                    print(f"      - $('Config Global').first().json.{field}")
                    print(f"        → $json.config.{field}")
        else:
            print(f"   ⚠️  No standard references found (may use different pattern)")

    return updated_count

def main():
    print("🚀 Updating Config Global references\n")

    # Load workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow loaded: {len(workflow['nodes'])} nodes\n")
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

    # Update references
    updated = update_config_references(workflow)

    if updated > 0:
        # Save workflow
        try:
            with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Workflow saved: {len(workflow['nodes'])} nodes")
        except Exception as e:
            print(f"\n❌ Error saving workflow: {e}")
            sys.exit(1)

    print("\n" + "=" * 80)
    print("CONFIG REFERENCE UPDATE COMPLETED")
    print("=" * 80)
    print(f"\nNodes updated: {updated}")

    if updated > 0:
        print("\n🎯 All Config Global references updated!")
        print("   Nodes now use: $json.config.FIELD_NAME")
    else:
        print("\nℹ️  No references needed updating")

if __name__ == '__main__':
    main()
