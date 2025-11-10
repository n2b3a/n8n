#!/usr/bin/env python3
"""
FIX: Connect AI Agent nodes to their Model and Memory sub-nodes

PROBLEM:
All AI Agent nodes are missing their model and memory sub-node references.
This causes the OpenAI Chat Model and Simple Memory nodes to be disconnected.

SOLUTION:
Add the proper __rl (resource locator) references to each agent node.
"""

import json
import sys

# Mapping of agents to their model and memory nodes
AGENT_MAPPINGS = {
    'Onboarding Agent': {
        'model': 'OpenAI Chat Model',
        'memory': 'Simple Memory'
    },
    'Agente de Compras': {
        'model': 'OpenAI Chat Model1',
        'memory': 'Simple Memory1'
    },
    'Agente de Setup': {
        'model': 'OpenAI Chat Model2',
        'memory': 'Simple Memory2'
    },
    'Extraer JSON de Preferencias': {
        'model': 'OpenAI Chat Model3',
        'memory': 'Simple Memory3'
    },
    'Agente de Menú Principal': {
        'model': 'OpenAI Chat Model4',
        'memory': 'Simple Memory4'
    },
    'Agente Subir Precios': {
        'model': 'OpenAI Chat Model5',
        'memory': 'Simple Memory5'
    },
    'Agente Config Produtos': {
        'model': 'OpenAI Config Produtos',
        'memory': 'Memory Config Produtos'
    },
    'Agente Registrar Fornecedor': {
        'model': 'OpenAI Register Fornecedor',
        'memory': 'Memory Register Fornecedor'
    }
}

def create_resource_locator(node_name):
    """Create a resource locator reference for a sub-node"""
    return {
        "__rl": {
            "value": node_name,
            "mode": "name",
            "cachedResultName": node_name
        }
    }

def fix_agent_connections(workflow):
    """Connect all AI Agent nodes to their model and memory sub-nodes"""
    print("=" * 80)
    print("FIXING AI AGENT NODE CONNECTIONS")
    print("=" * 80)

    nodes = workflow['nodes']
    fixed_count = 0

    for node in nodes:
        name = node['name']

        if name not in AGENT_MAPPINGS:
            continue

        print(f'\n🔧 Fixing: {name}')

        mapping = AGENT_MAPPINGS[name]
        params = node.get('parameters', {})

        # Add model reference
        model_name = mapping['model']
        params['model'] = create_resource_locator(model_name)
        print(f'   ✅ Connected to model: {model_name}')

        # Add memory reference
        memory_name = mapping['memory']
        params['memory'] = create_resource_locator(memory_name)
        print(f'   ✅ Connected to memory: {memory_name}')

        fixed_count += 1

    return fixed_count

def main():
    print("🚀 Fixing AI Agent connections\n")

    # Load workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow loaded: {len(workflow['nodes'])} nodes\n")
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

    # Fix AI Agent connections
    fixed = fix_agent_connections(workflow)

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
    print("AI AGENT CONNECTIONS FIX COMPLETED")
    print("=" * 80)
    print(f"\nAgents fixed: {fixed}/8")

    if fixed == 8:
        print("\n🎯 All AI Agent nodes now properly connected to their models and memories!")
    else:
        print(f"\n⚠️  Only {fixed} agents were fixed. Expected 8.")

if __name__ == '__main__':
    main()
