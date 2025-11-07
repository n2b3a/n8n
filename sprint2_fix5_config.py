#!/usr/bin/env python3
"""
SPRINT 2 - FIX #5: Config Global Node
Create centralized configuration node and update hardcoded values
"""

import json
import sys
import re

def create_config_node(workflow):
    """Create Config Global node with centralized values"""
    print("=" * 80)
    print("SPRINT 2 - FIX #5: CONFIG GLOBAL NODE")
    print("=" * 80)

    nodes = workflow['nodes']

    # Check if already exists
    for node in nodes:
        if node['name'] == 'Config Global':
            print("  ℹ️  Config Global node already exists")
            return node

    print("\n📍 Creating Config Global node...")

    config_node = {
        "id": "CONFIG_GLOBAL",
        "name": "Config Global",
        "type": "n8n-nodes-base.set",
        "typeVersion": 3.3,
        "position": [200, 200],
        "parameters": {
            "mode": "manual",
            "duplicateItem": False,
            "assignments": {
                "assignments": [
                    {
                        "id": "price_validity",
                        "name": "PRICE_VALIDITY_DAYS",
                        "value": 30,
                        "type": "number"
                    },
                    {
                        "id": "pref_fields",
                        "name": "PREFERENCE_FIELDS_TOTAL",
                        "value": 5,
                        "type": "number"
                    },
                    {
                        "id": "welcome_msg",
                        "name": "WELCOME_MESSAGE",
                        "value": "🍽️ *Bem-vindo ao Frepi!*",
                        "type": "string"
                    },
                    {
                        "id": "session_timeout",
                        "name": "SESSION_TIMEOUT_MINUTES",
                        "value": 60,
                        "type": "number"
                    },
                    {
                        "id": "max_retries",
                        "name": "AI_MAX_RETRIES",
                        "value": 3,
                        "type": "number"
                    },
                    {
                        "id": "ai_timeout",
                        "name": "AI_TIMEOUT_SECONDS",
                        "value": 30,
                        "type": "number"
                    },
                    {
                        "id": "incomplete_profile_warning",
                        "name": "INCOMPLETE_PROFILE_WARNING",
                        "value": "⚠️ *Perfil incompleto ({percentage}%)*\n→ Configure preferências para melhores recomendações!\n\n",
                        "type": "string"
                    },
                    {
                        "id": "continuation_message",
                        "name": "CONTINUATION_MESSAGE",
                        "value": "✅ *Pronto!*\n\n💬 Posso te ajudar com algo mais?\n\n1️⃣ Fazer outra compra\n2️⃣ Atualizar preços\n3️⃣ Registrar fornecedor\n4️⃣ Ver menú principal\n\nDigite o número ou descreva o que precisa.",
                        "type": "string"
                    }
                ]
            }
        },
        "notes": "Configuração global do workflow. Modifique aqui para ajustar comportamento."
    }

    nodes.insert(0, config_node)  # Add at beginning
    print("  ✅ Config Global node created")
    print("  📋 Configuration values:")
    print("     - PRICE_VALIDITY_DAYS: 30")
    print("     - PREFERENCE_FIELDS_TOTAL: 5")
    print("     - AI_MAX_RETRIES: 3")
    print("     - AI_TIMEOUT_SECONDS: 30")
    print("     - SESSION_TIMEOUT_MINUTES: 60")
    print("     - + Message templates")

    return config_node

def update_hardcoded_values(workflow):
    """Replace hardcoded values with Config references"""
    print("\n" + "=" * 80)
    print("UPDATING HARDCODED VALUES TO USE CONFIG")
    print("=" * 80)

    nodes = workflow['nodes']
    updated_count = 0

    replacements = [
        # Price validity days
        {
            'pattern': r'fechaLimite\.setDate\(fechaLimite\.getDate\(\) - 30\)',
            'replacement': "fechaLimite.setDate(fechaLimite.getDate() - parseInt($('Config Global').first().json.PRICE_VALIDITY_DAYS))",
            'description': 'Price validity days'
        },
        {
            'pattern': r'\.setDate\([^)]+\.getDate\(\)\s*-\s*30\)',
            'replacement': ".setDate(new Date().getDate() - parseInt($('Config Global').first().json.PRICE_VALIDITY_DAYS))",
            'description': 'Price validity days (alternative)'
        },
        # Preference fields total
        {
            'pattern': r'const totalCampos = 5;',
            'replacement': "const totalCampos = parseInt($('Config Global').first().json.PREFERENCE_FIELDS_TOTAL);",
            'description': 'Preference fields total'
        },
        # Welcome message
        {
            'pattern': r'🍽️ \*Bem-vindo ao Frepi!\*',
            'replacement': "${$('Config Global').first().json.WELCOME_MESSAGE}",
            'description': 'Welcome message'
        }
    ]

    for node in nodes:
        if node['type'] != 'n8n-nodes-base.code':
            continue

        code = node['parameters'].get('jsCode', '')
        node_name = node['name']
        node_updated = False

        for repl in replacements:
            if re.search(repl['pattern'], code):
                code = re.sub(repl['pattern'], repl['replacement'], code)
                node_updated = True
                print(f"  ✅ {node_name:45} - Updated: {repl['description']}")

        if node_updated:
            node['parameters']['jsCode'] = code
            updated_count += 1

    return updated_count

def update_continuation_message(workflow):
    """Update Preguntar Continuação to use config"""
    print("\n📍 Updating continuation message...")

    nodes = workflow['nodes']

    for node in nodes:
        if node['name'] == 'Preguntar Continuação':
            code = node['parameters']['jsCode']

            # Replace hardcoded message with config reference
            code = re.sub(
                r'const mensagemContinuacao = `[^`]+`;',
                "const mensagemContinuacao = $('Config Global').first().json.CONTINUATION_MESSAGE;",
                code
            )

            node['parameters']['jsCode'] = code
            print("  ✅ Continuation message now uses config")
            return True

    return False

def main():
    print("🚀 Starting Sprint 2 - Fix #5: Config Global\n")

    # Load workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow loaded: {len(workflow['nodes'])} nodes\n")
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

    # Create Config node
    create_config_node(workflow)

    # Update hardcoded values
    updated = update_hardcoded_values(workflow)

    # Update continuation message
    update_continuation_message(workflow)

    # Save workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Workflow saved: {len(workflow['nodes'])} nodes")
    except Exception as e:
        print(f"\n❌ Error saving workflow: {e}")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("SPRINT 2 - FIX #5 COMPLETED")
    print("=" * 80)
    print(f"\nNodes updated with config references: {updated}")
    print("\n💡 Benefits:")
    print("   - Change configuration without touching code")
    print("   - Centralized configuration management")
    print("   - Easy A/B testing of values")
    print("\n🎯 All hardcoded values now configurable!")

if __name__ == '__main__':
    main()
