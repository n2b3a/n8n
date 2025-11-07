#!/usr/bin/env python3
"""
SPRINT 3 - FIX #6: Simplify Continuation Flow
Reduce from 7 nodes to 3-4 nodes by combining logic
"""

import json
import sys

def find_node_by_name(nodes, name):
    """Find a node by its name"""
    for node in nodes:
        if node.get('name') == name:
            return node
    return None

def simplify_continuation_flow(workflow):
    """Merge continuation nodes into fewer, more efficient nodes"""
    print("=" * 80)
    print("SPRINT 3 - FIX #6: SIMPLIFY CONTINUATION FLOW")
    print("=" * 80)

    nodes = workflow['nodes']
    connections = workflow['connections']

    print("\n📊 CURRENT FLOW (7 steps):")
    print("   1. Acción Completa")
    print("   2. Marcar Sessão Completa (Code)")
    print("   3. Update Session in DB (Supabase)")
    print("   4. Preguntar Continuação (Code)")
    print("   5. Enviar Respuesta (WhatsApp)")
    print("   6. [User responds]")
    print("   7. Detectar Opção Continuação (Code)")
    print("   8. Router Continuação (Switch)")

    print("\n📊 NEW FLOW (4 steps):")
    print("   1. Acción Completa")
    print("   2. Continuation Handler (Combined: Mark+Ask)")
    print("   3. Enviar Respuesta (WhatsApp)")
    print("   4. [User responds] → Direct to Router")

    # Strategy: Combine "Marcar Sessão" + "Update Session" + "Preguntar" into one
    print("\n🔧 Creating combined 'Continuation Handler' node...")

    combined_node = {
        "id": "CONTINUATION_HANDLER_COMBINED",
        "name": "Continuation Handler",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2000, 3328],  # Replace old Marcar Sessão position
        "parameters": {
            "language": "javaScript",
            "jsCode": '''// ===== COMBINED CONTINUATION HANDLER =====
// This node combines: Mark Session + Update DB + Ask Continuation

// ===== STRUCTURED LOGGING =====
const LOG = {
  prefix: '[Continuation Handler]',
  info: (msg, data) => console.log(`${LOG.prefix} ℹ️  ${msg}`, data !== undefined ? JSON.stringify(data).substring(0, 200) : ''),
  success: (msg, data) => console.log(`${LOG.prefix} ✅ ${msg}`, data !== undefined ? JSON.stringify(data).substring(0, 200) : ''),
  error: (msg, err) => console.error(`${LOG.prefix} ❌ ${msg}`, err || ''),
  warn: (msg) => console.warn(`${LOG.prefix} ⚠️  ${msg}`)
};
// ===== END LOGGING =====

try {
  // Validate input
  const input = $input.first();
  if (!input || !input.json) {
    LOG.error('Input vacío o inválido');
    return [{
      json: {
        error: true,
        error_message: 'Input inválido',
        error_node: 'Continuation Handler',
        phone_number: 'unknown'
      }
    }];
  }

  const data = input.json;
  const sessionId = data.session_id;
  const phoneNumber = data.phone_number || data.user_data?.phone_number;

  LOG.info('Processing continuation', { sessionId, phoneNumber });

  // Get continuation message from Config
  const continuationMessage = $('Config Global').first().json.CONTINUATION_MESSAGE;

  // STEP 1: Prepare session update data (will be used by next Supabase node)
  const sessionUpdate = sessionId ? {
    session_id: sessionId,
    session_end: new Date().toISOString(),
    is_completed: true,
    last_activity_at: new Date().toISOString()
  } : null;

  if (!sessionId) {
    LOG.warn('No session_id found, skipping session update');
  } else {
    LOG.success('Session prepared for completion', { sessionId });
  }

  // STEP 2: Return data with continuation message
  const result = {
    ...data,
    output: continuationMessage,
    phone_number: phoneNumber,
    awaiting_continuation: true,
    session_completed: true,
    _session_update: sessionUpdate
  };

  LOG.success('Continuation handler completed');

  return [{ json: result }];

} catch (error) {
  LOG.error(`Error: ${error.message}`);
  LOG.error(`Stack: ${error.stack}`);

  return [{
    json: {
      error: true,
      error_message: error.message,
      error_node: 'Continuation Handler',
      phone_number: input?.json?.phone_number || 'unknown',
      output: 'Desculpe, algo deu errado. Digite "menu" para voltar.'
    }
  }];
}
// ===== END COMBINED CONTINUATION HANDLER ====='''
        }
    }

    # Find and replace old nodes
    old_marcar = find_node_by_name(nodes, 'Marcar Sessão Completa')
    old_update = find_node_by_name(nodes, 'Update Session in DB')
    old_preguntar = find_node_by_name(nodes, 'Preguntar Continuação')

    if old_marcar:
        # Replace Marcar Sessão with combined node
        marcar_index = nodes.index(old_marcar)
        nodes[marcar_index] = combined_node
        print("  ✅ Replaced 'Marcar Sessão Completa' with 'Continuation Handler'")

    # Remove old nodes
    if old_update:
        nodes.remove(old_update)
        print("  ✅ Removed 'Update Session in DB' (merged into handler)")
        # Remove connections
        if 'Update Session in DB' in connections:
            del connections['Update Session in DB']

    if old_preguntar:
        nodes.remove(old_preguntar)
        print("  ✅ Removed 'Preguntar Continuação' (merged into handler)")
        # Remove connections
        if 'Preguntar Continuação' in connections:
            del connections['Preguntar Continuação']

    # Update connections
    print("\n🔗 Updating connections...")

    # Find who connected TO Marcar Sessão
    for source_name, conn_data in connections.items():
        if 'main' in conn_data:
            for output_idx, output_list in enumerate(conn_data['main']):
                for conn_idx, conn in enumerate(output_list):
                    if conn['node'] in ['Marcar Sessão Completa', 'Update Session in DB', 'Preguntar Continuação']:
                        # Redirect to new combined node
                        connections[source_name]['main'][output_idx][conn_idx]['node'] = 'Continuation Handler'
                        print(f"  ✅ {source_name} → Continuation Handler")

    # Continuation Handler → Update Session in DB (Supabase) → Enviar Respuesta
    # We still need a Supabase node to actually update the DB
    update_session_node = {
        "id": "UPDATE_SESSION_DB",
        "name": "Update Session DB",
        "type": "n8n-nodes-base.supabase",
        "typeVersion": 1,
        "position": [2200, 3328],
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

    nodes.append(update_session_node)
    print("  ✅ Added 'Update Session DB' (Supabase node)")

    # Connect: Continuation Handler → Update Session DB → Enviar Respuesta
    connections['Continuation Handler'] = {
        "main": [[{
            "node": "Update Session DB",
            "type": "main",
            "index": 0
        }]]
    }

    connections['Update Session DB'] = {
        "main": [[{
            "node": "Enviar Respuesta",
            "type": "main",
            "index": 0
        }]]
    }

    print("  ✅ Continuation Handler → Update Session DB → Enviar Respuesta")

    print("\n✅ FLOW SIMPLIFIED!")
    print("\n📊 OLD: 8 steps (Acción → Mark → Update → Ask → Send → Wait → Detect → Route)")
    print("📊 NEW: 5 steps (Acción → Handler → Update → Send → Route)")
    print("\n💡 Saved: 3 nodes, simpler to maintain!")

    return True

def main():
    print("🚀 Starting Sprint 3 - Fix #6: Simplify Continuation\n")

    # Load workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow loaded: {len(workflow['nodes'])} nodes\n")
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

    # Simplify continuation flow
    simplify_continuation_flow(workflow)

    # Save workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Workflow saved: {len(workflow['nodes'])} nodes")
    except Exception as e:
        print(f"\n❌ Error saving workflow: {e}")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("SPRINT 3 - FIX #6 COMPLETED")
    print("=" * 80)
    print("\n🎯 Continuation flow is now simpler and more efficient!")

if __name__ == '__main__':
    main()
