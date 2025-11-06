#!/usr/bin/env python3
"""
Add routing logic to handle duplicate supplier decision responses.
The user needs to be routed to HANDLE_DUPLICATE_SUPPLIER_DECISION when they
respond to a duplicate warning.
"""

import json

def find_node_by_name(nodes, name):
    """Find a node by its name"""
    for node in nodes:
        if node.get('name') == name:
            return node
    return None

def main():
    print("🔧 Adding duplicate decision routing...\n")

    # Load workflow
    with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
        workflow = json.load(f)
    print(f"✅ Loaded workflow with {len(workflow['nodes'])} nodes\n")

    # Strategy: Update the AGENT_REGISTER_FORNECEDOR to be aware of duplicate scenarios
    # and handle the user's follow-up responses

    agent_fornecedor = find_node_by_name(workflow['nodes'], 'AGENT_REGISTER_FORNECEDOR')
    if agent_fornecedor:
        # Update the agent's system prompt to handle duplicate decisions
        current_prompt = agent_fornecedor['parameters']['options']['systemMessage']

        # Add instructions for handling duplicate scenarios
        enhanced_prompt = current_prompt + '''

---

⚠️ IMPORTANTE - CENÁRIO DE DUPLICADO:

Se o usuário está respondendo a uma mensagem de fornecedor duplicado (opções 1, 2 ou 3):

Opção 1: "Criar novo fornecedor mesmo assim"
Opção 2: "Atualizar dados do primeiro da lista"
Opção 3: "Cancelar"

FORMATO DE RESPOSTA:
DECISAO_DUPLICADO:[1|2|3]

Exemplo:
Usuario: "1"
Você: DECISAO_DUPLICADO:1

Usuario: "atualizar o existente"
Você: DECISAO_DUPLICADO:2

TOM: Confirme a ação escolhida de forma clara.'''

        agent_fornecedor['parameters']['options']['systemMessage'] = enhanced_prompt
        print("  ✅ Enhanced AGENT_REGISTER_FORNECEDOR to handle duplicate decisions")

    # Add a detector node to check if the agent output is a duplicate decision
    max_pos_y = max([node['position'][1] for node in workflow['nodes']])

    detect_duplicate_decision = {
        "id": "DETECT_DUPLICATE_DECISION",
        "name": "Detectar Decisión Duplicado",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1500, max_pos_y + 200],
        "parameters": {
            "language": "javaScript",
            "jsCode": '''const input = $input.first().json;
const output = input.output || '';

console.log(`🔍 [Detectar Decisión] Output: ${output.substring(0, 100)}...`);

// Check if this is a duplicate decision response
if (output.includes('DECISAO_DUPLICADO:')) {
  const match = output.match(/DECISAO_DUPLICADO:(\\d)/);
  if (match) {
    const decision = match[1];
    console.log(`✅ [Detectar Decisión] Detectada decisión de duplicado: ${decision}`);

    return [{
      json: {
        ...input,
        is_duplicate_decision: true,
        duplicate_choice: decision,
        message: decision, // Simulate user message for handler
        output_route: 0  // Route to handler
      }
    }];
  }
}

// Not a duplicate decision - continue normal flow
console.log(`➡️ [Detectar Decisión] No es decisión de duplicado, flujo normal`);
return [{
  json: {
    ...input,
    is_duplicate_decision: false,
    output_route: 1  // Route to normal save
  }
}];'''
        }
    }

    workflow['nodes'].append(detect_duplicate_decision)
    print("  ✅ Added 'Detectar Decisión Duplicado' node")

    # Add a router to split the flow
    router_duplicate_decision = {
        "id": "ROUTER_DUPLICATE_DECISION",
        "name": "Router: ¿Es Decisión Duplicado?",
        "type": "n8n-nodes-base.switch",
        "typeVersion": 3,
        "position": [1700, max_pos_y + 200],
        "parameters": {
            "rules": {
                "rules": [
                    {
                        "conditions": {
                            "boolean": [
                                {
                                    "value1": "={{ $json.is_duplicate_decision }}",
                                    "value2": True
                                }
                            ]
                        },
                        "renameOutput": False
                    }
                ]
            },
            "options": {}
        }
    }

    workflow['nodes'].append(router_duplicate_decision)
    print("  ✅ Added 'Router: ¿Es Decisión Duplicado?' node")

    # Update connections:
    # AGENT_REGISTER_FORNECEDOR -> DETECT_DUPLICATE_DECISION -> ROUTER -> [HANDLE_DUPLICATE or SAVE_FORNECEDOR_DB]

    # Find current connection from AGENT_REGISTER_FORNECEDOR
    if 'AGENT_REGISTER_FORNECEDOR' in workflow['connections']:
        original_target = workflow['connections']['AGENT_REGISTER_FORNECEDOR']['main'][0][0]['node']
        print(f"  📌 Original: AGENT_REGISTER_FORNECEDOR -> {original_target}")

        # Redirect through detector
        workflow['connections']['AGENT_REGISTER_FORNECEDOR'] = {
            "main": [
                [
                    {
                        "node": "DETECT_DUPLICATE_DECISION",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }

        # Detector to router
        workflow['connections']['DETECT_DUPLICATE_DECISION'] = {
            "main": [
                [
                    {
                        "node": "ROUTER_DUPLICATE_DECISION",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }

        # Router splits:
        # Output 0 (is_duplicate_decision=true) -> HANDLE_DUPLICATE_SUPPLIER_DECISION
        # Output 1 (is_duplicate_decision=false) -> original target (SAVE_FORNECEDOR_DB)
        workflow['connections']['ROUTER_DUPLICATE_DECISION'] = {
            "main": [
                [
                    {
                        "node": "HANDLE_DUPLICATE_SUPPLIER_DECISION",
                        "type": "main",
                        "index": 0
                    }
                ],
                [
                    {
                        "node": original_target,
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }

        print("  ✅ Connections updated: AGENT -> DETECTOR -> ROUTER -> [HANDLER | SAVE]")

    # Save
    with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved updated workflow with {len(workflow['nodes'])} nodes")
    print("✨ Duplicate routing complete!")

if __name__ == '__main__':
    main()
