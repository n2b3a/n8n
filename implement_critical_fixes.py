#!/usr/bin/env python3
"""
SPRINT 1: CRITICAL FIXES
1. Replace $supabase Code node with HTTP Request node
2. Add try-catch to all Code nodes
3. Validate inputs before use
"""

import json
import sys

def find_node_by_name(nodes, name):
    """Find a node by its name"""
    for node in nodes:
        if node.get('name') == name:
            return node
    return None

def fix_marcar_sessao_node(workflow):
    """Replace Code node with Supabase HTTP Request node"""
    print("=" * 80)
    print("FIX 1: REEMPLAZAR MARCAR SESSÃO COMPLETA")
    print("=" * 80)

    nodes = workflow['nodes']
    connections = workflow['connections']

    # Find the problematic node
    marcar_node = find_node_by_name(nodes, 'Marcar Sessão Completa')
    if not marcar_node:
        print("⚠️  Node not found")
        return False

    print(f"\n📍 Found node at position {marcar_node['position']}")

    # Get current connections
    incoming = None
    outgoing = connections.get('Marcar Sessão Completa', {})

    # Find who connects TO this node
    for source_name, conn_data in connections.items():
        if 'main' in conn_data:
            for output_list in conn_data['main']:
                for conn in output_list:
                    if conn['node'] == 'Marcar Sessão Completa':
                        incoming = source_name
                        break

    print(f"  Incoming from: {incoming}")
    print(f"  Outgoing to: {outgoing}")

    # Replace with corrected Code node that doesn't use $supabase
    # Instead, we'll update the session in the NEXT Supabase operation
    # Or create a proper HTTP Request node

    new_code = '''// FIXED: No usar $supabase directamente
// En su lugar, preparamos los datos para el siguiente nodo

const input = $input.first();

// Validación de input
if (!input || !input.json) {
  console.error('[Marcar Sessão] Input vacío o inválido');
  return [{
    json: {
      error: true,
      message: 'Erro interno: input inválido',
      phone_number: 'unknown'
    }
  }];
}

const data = input.json;
const sessionId = data.session_id;
const phoneNumber = data.phone_number || data.user_data?.phone_number;

console.log(`✅ [Marcar Sessão] Preparando para marcar sesión: ${sessionId || 'N/A'}`);

if (!sessionId) {
  console.warn('[Marcar Sessão] No session_id found, skipping update');
}

// Pasar datos al siguiente nodo CON los campos de actualización
return [{
  json: {
    ...data,
    session_completed: true,
    // Estos campos se usarán en el Supabase node siguiente
    _session_update: sessionId ? {
      session_id: sessionId,
      session_end: new Date().toISOString(),
      is_completed: true,
      last_activity_at: new Date().toISOString()
    } : null
  }
}];'''

    marcar_node['parameters']['jsCode'] = new_code
    print("  ✅ Code updated - No longer uses $supabase")

    # Ahora agregar un Supabase node real después de este
    max_y = max([n['position'][1] for n in nodes])

    supabase_update_node = {
        "id": "UPDATE_SESSION_SUPABASE",
        "name": "Update Session in DB",
        "type": "n8n-nodes-base.supabase",
        "typeVersion": 1,
        "position": [marcar_node['position'][0] + 200, marcar_node['position'][1]],
        "parameters": {
            "resource": "row",
            "operation": "update",
            "tableId": "line_sessions",
            "filterType": "manual",
            "filterBy": "={{ $json._session_update ? $json._session_update.session_id : null }}",
            "fieldsUi": {
                "fieldValues": [
                    {
                        "fieldId": "session_end",
                        "fieldValue": "={{ $json._session_update ? $json._session_update.session_end : $now }}"
                    },
                    {
                        "fieldId": "is_completed",
                        "fieldValue": "={{ $json._session_update ? true : false }}"
                    },
                    {
                        "fieldId": "last_activity_at",
                        "fieldValue": "={{ $json._session_update ? $json._session_update.last_activity_at : $now }}"
                    }
                ]
            }
        }
    }

    nodes.append(supabase_update_node)
    print(f"  ✅ Added Supabase Update node")

    # Update connections: Marcar Sessão → Update Session → Preguntar
    old_target = outgoing.get('main', [[]])[0]
    if old_target:
        target_node = old_target[0]['node']

        # Marcar Sessão → Update Session
        connections['Marcar Sessão Completa'] = {
            "main": [
                [
                    {
                        "node": "Update Session in DB",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }

        # Update Session → Original target
        connections['Update Session in DB'] = {
            "main": [
                [
                    {
                        "node": target_node,
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }

        print(f"  ✅ Connections updated: Marcar → Update → {target_node}")

    return True

def add_error_handling_to_code_nodes(workflow):
    """Add try-catch and input validation to all Code nodes"""
    print("\n" + "=" * 80)
    print("FIX 2 & 3: ERROR HANDLING + INPUT VALIDATION")
    print("=" * 80)

    nodes = workflow['nodes']
    fixed_count = 0

    for node in nodes:
        if node['type'] != 'n8n-nodes-base.code':
            continue

        # Skip if it's a simple passthrough
        code = node['parameters'].get('jsCode', '')
        if len(code) < 50:  # Too short to need error handling
            continue

        # Check if already has try-catch
        if 'try {' in code:
            print(f"  ℹ️  {node['name']:40} - Already has try-catch")
            continue

        print(f"\n🔧 Adding error handling: {node['name']}")

        # Wrap entire code in try-catch with input validation
        wrapped_code = f'''// ===== ERROR HANDLING & INPUT VALIDATION =====
try {{
  // Validate input
  const input = $input.first();
  if (!input || !input.json) {{
    console.error('[{node['name']}] Input vacío o inválido');
    return [{{
      json: {{
        error: true,
        error_message: 'Input inválido',
        error_node: '{node['name']}',
        phone_number: 'unknown'
      }}
    }}];
  }}

  // Original code starts here
  {code}

}} catch (error) {{
  console.error(`[{node['name']}] Error: ${{error.message}}`);
  console.error(`[{node['name']}] Stack: ${{error.stack}}`);

  return [{{
    json: {{
      error: true,
      error_message: error.message,
      error_node: '{node['name']}',
      phone_number: input?.json?.phone_number || input?.json?.user_data?.phone_number || 'unknown',
      output: 'Desculpe, algo deu errado. Por favor, tente novamente ou digite "menu" para voltar.'
    }}
  }}];
}}
// ===== END ERROR HANDLING ====='''

        node['parameters']['jsCode'] = wrapped_code
        fixed_count += 1
        print(f"  ✅ Error handling added")

    return fixed_count

def add_global_error_handler(workflow):
    """Add a global error handler node"""
    print("\n" + "=" * 80)
    print("FIX 4: GLOBAL ERROR HANDLER")
    print("=" * 80)

    nodes = workflow['nodes']
    max_y = max([n['position'][1] for n in nodes])

    error_handler = {
        "id": "GLOBAL_ERROR_HANDLER",
        "name": "Global Error Handler",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2400, max_y + 400],
        "parameters": {
            "language": "javaScript",
            "jsCode": '''// Global Error Handler
const input = $input.first();
const error = input?.json?.error_message || 'Erro desconhecido';
const errorNode = input?.json?.error_node || 'Unknown';
const phoneNumber = input?.json?.phone_number || 'unknown';

console.error(`[Global Error Handler] Error from ${errorNode}: ${error}`);

// Log to metrics/monitoring (if available)
// await logError(errorNode, error, phoneNumber);

const errorMessage = `❌ *Desculpe, algo deu errado.*

Tente novamente ou digite *"menu"* para voltar ao início.

Código do erro: ${errorNode}`;

return [{
  json: {
    output: errorMessage,
    phone_number: phoneNumber,
    is_error: true
  }
}];'''
        }
    }

    nodes.append(error_handler)
    print("  ✅ Global Error Handler created")

    # Connect to Enviar Respuesta
    workflow['connections']['Global Error Handler'] = {
        "main": [
            [
                {
                    "node": "Enviar Respuesta",
                    "type": "main",
                    "index": 0
                }
            ]
        ]
    }
    print("  ✅ Connected to Enviar Respuesta")

    return True

def main():
    print("🚀 Implementing Critical Fixes (Sprint 1)\n")

    # Load workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow loaded: {len(workflow['nodes'])} nodes\n")
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

    # Apply fixes
    fix_marcar_sessao_node(workflow)

    fixed_code_nodes = add_error_handling_to_code_nodes(workflow)

    add_global_error_handler(workflow)

    # Save workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Workflow saved: {len(workflow['nodes'])} nodes")
    except Exception as e:
        print(f"\n❌ Error saving workflow: {e}")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("CRITICAL FIXES COMPLETED")
    print("=" * 80)
    print("\nChanges made:")
    print(f"  ✅ Marcar Sessão Completa: Now uses proper Supabase node")
    print(f"  ✅ Code nodes with error handling: {fixed_code_nodes}")
    print(f"  ✅ Global Error Handler: Created")
    print(f"\nTotal nodes: {len(workflow['nodes'])}")
    print("\n🎯 Workflow is now more robust and production-ready!")

if __name__ == '__main__':
    main()
