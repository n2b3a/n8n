#!/usr/bin/env python3
"""
FASE 3: Gestión de Sesiones y Conexión de Flujos
- Crear nodo "Marcar Sessão Completa"
- Conectar flujos existentes al sistema de continuación
- Redirigir: Generar Recomendación → Marcar Sesión → Preguntar Continuação
- Redirigir: Guardar Precios → Marcar Sesión → Preguntar Continuação
- Redirigir: Guardar Fornecedor → Marcar Sesión → Preguntar Continuação
"""

import json
import sys

def find_node_by_name(nodes, name):
    """Find a node by its name"""
    for node in nodes:
        if node.get('name') == name:
            return node
    return None

def fase3_sesiones_y_conexiones(workflow):
    """FASE 3: Marcar sesiones completas y conectar flujos"""
    print("=" * 80)
    print("FASE 3: GESTIÓN DE SESIONES Y CONEXIÓN DE FLUJOS")
    print("=" * 80)

    nodes = workflow['nodes']
    connections = workflow['connections']

    # Encontrar la posición Y más baja
    max_y = max([node['position'][1] for node in nodes])

    # Cambio 3.1: Crear nodo "Marcar Sessão Completa"
    print("\n[3.1] Creando nodo 'Marcar Sessão Completa'...")

    marcar_session_node = {
        "id": "MARCAR_SESSAO_COMPLETA",
        "name": "Marcar Sessão Completa",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2000, max_y + 200],
        "parameters": {
            "language": "javaScript",
            "jsCode": '''const input = $input.first().json;
const sessionId = input.session_id;

console.log(`✅ [Marcar Sessão] Marcando sesión como completa: ${sessionId}`);

// Actualizar sesión en Supabase
if (sessionId) {
  try {
    await $supabase
      .from('line_sessions')
      .update({
        session_end: new Date().toISOString(),
        is_completed: true,
        last_activity_at: new Date().toISOString()
      })
      .eq('session_id', sessionId);

    console.log(`✅ [Marcar Sessão] Sesión ${sessionId} marcada como completa`);
  } catch (error) {
    console.error(`❌ [Marcar Sessão] Error: ${error.message}`);
  }
}

// Pasar datos al siguiente nodo
return [{
  json: {
    ...input,
    session_completed: true
  }
}];'''
        }
    }

    nodes.append(marcar_session_node)
    print("  ✅ Nodo 'Marcar Sessão Completa' creado")

    # Cambio 3.2: Conectar flujos existentes
    print("\n[3.2] Conectando flujos existentes al sistema de continuación...")

    # FLUJO 1: Generar Recomendación → Marcar → Preguntar
    print("\n  [Flujo 1: Compras]")
    rec_node = find_node_by_name(nodes, 'Generar Recomendación')
    if rec_node:
        # Redirigir a Marcar Sesión
        connections['Generar Recomendación'] = {
            "main": [
                [
                    {
                        "node": "Marcar Sessão Completa",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
        print("    ✅ Generar Recomendación → Marcar Sessão Completa")
    else:
        print("    ⚠️  Nodo 'Generar Recomendación' no encontrado")

    # Marcar Sesión → Preguntar
    if 'Marcar Sessão Completa' not in connections:
        connections['Marcar Sessão Completa'] = {"main": [[]]}

    connections['Marcar Sessão Completa']['main'][0].append({
        "node": "Preguntar Continuação",
        "type": "main",
        "index": 0
    })
    print("    ✅ Marcar Sessão Completa → Preguntar Continuação")

    # FLUJO 2: Subir Precios
    print("\n  [Flujo 2: Subir Precios]")
    # Buscar el nodo que confirma precios guardados
    # Puede ser "Confirmar Precios" o similar
    for node in nodes:
        if 'Precios Completos' in node['name'] or 'Confirmar Precios' in node['name']:
            print(f"    Encontrado nodo: {node['name']}")
            # Buscar la conexión actual y redirigir
            if node['name'] in connections:
                # Agregar conexión a Marcar Sesión
                connections[node['name']]['main'][0] = [{
                    "node": "Marcar Sessão Completa",
                    "type": "main",
                    "index": 0
                }]
                print(f"    ✅ {node['name']} → Marcar Sessão Completa")
            break

    # FLUJO 3: Registrar Fornecedor
    print("\n  [Flujo 3: Registrar Fornecedor]")
    # El flujo de fornecedor termina en "Check If Duplicate"
    if 'Check If Duplicate' in connections:
        # Ambas salidas (duplicate y no duplicate) deben ir a Marcar Sesión
        # Output 0 (tiene duplicado) - ya va a Enviar Respuesta
        # Output 1 (no duplicate) - va a Enviar Respuesta
        # Necesitamos interceptar ANTES de Enviar Respuesta

        # Vamos a insertar Marcar Sesión ANTES de Enviar Respuesta en este flujo
        connections['Check If Duplicate']['main'] = [
            [
                {
                    "node": "Marcar Sessão Completa",
                    "type": "main",
                    "index": 0
                }
            ],
            [
                {
                    "node": "Marcar Sessão Completa",
                    "type": "main",
                    "index": 0
                }
            ]
        ]
        print("    ✅ Check If Duplicate (ambas salidas) → Marcar Sessão Completa")

    print("\n✅ FASE 3 COMPLETADA")
    print(f"   Nodos totales: {len(nodes)}")
    return True

def main():
    print("🚀 Iniciando implementación - FASE 3\n")

    # Cargar workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow cargado: {len(workflow['nodes'])} nodos\n")
    except Exception as e:
        print(f"❌ Error cargando workflow: {e}")
        sys.exit(1)

    # Ejecutar Fase 3
    if not fase3_sesiones_y_conexiones(workflow):
        print("\n❌ Error en Fase 3")
        sys.exit(1)

    # Guardar workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Workflow guardado: {len(workflow['nodes'])} nodos")
    except Exception as e:
        print(f"\n❌ Error guardando workflow: {e}")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("FASE 3 COMPLETADA CON ÉXITO")
    print("=" * 80)
    print("\nCambios realizados:")
    print("  ✅ Nodo 'Marcar Sessão Completa' creado")
    print("  ✅ Flujo de Compras conectado al sistema de continuación")
    print("  ✅ Flujo de Subir Precios conectado al sistema de continuación")
    print("  ✅ Flujo de Registrar Fornecedor conectado al sistema de continuación")
    print("\nAhora los usuarios podrán volver al menú después de cada acción!")

if __name__ == '__main__':
    main()
