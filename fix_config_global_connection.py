#!/usr/bin/env python3
"""
FIX: Connect Config Global to the workflow execution flow
Config Global needs to execute BEFORE any node that references it
"""

import json
import sys

def connect_config_global(workflow):
    """Insert Config Global into the execution flow"""
    print("=" * 80)
    print("CONNECTING CONFIG GLOBAL TO WORKFLOW FLOW")
    print("=" * 80)

    connections = workflow['connections']

    # Current flow: WhatsApp Trigger → Extraer Datos WhatsApp
    # New flow: WhatsApp Trigger → Config Global → Extraer Datos WhatsApp

    print("\nCurrent flow:")
    print("  WhatsApp Trigger → Extraer Datos WhatsApp")
    print("\nNew flow:")
    print("  WhatsApp Trigger → Config Global → Extraer Datos WhatsApp")

    # Step 1: Connect WhatsApp Trigger → Config Global
    connections['WhatsApp Trigger'] = {
        "main": [[{
            "node": "Config Global",
            "type": "main",
            "index": 0
        }]]
    }
    print("\n✅ Connected: WhatsApp Trigger → Config Global")

    # Step 2: Connect Config Global → Extraer Datos WhatsApp
    connections['Config Global'] = {
        "main": [[{
            "node": "Extraer Datos WhatsApp",
            "type": "main",
            "index": 0
        }]]
    }
    print("✅ Connected: Config Global → Extraer Datos WhatsApp")

    return True

def main():
    print("🚀 Fixing Config Global connection\n")

    # Load workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow loaded: {len(workflow['nodes'])} nodes\n")
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

    # Connect Config Global
    connect_config_global(workflow)

    # Save workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Workflow saved: {len(workflow['nodes'])} nodes")
    except Exception as e:
        print(f"\n❌ Error saving workflow: {e}")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("CONFIG GLOBAL CONNECTION COMPLETED")
    print("=" * 80)
    print("\n🎯 Config Global is now connected to the workflow flow!")
    print("   It will execute at the start of every workflow run.")
    print("   All nodes can now reference: $('Config Global').first().json")

if __name__ == '__main__':
    main()
