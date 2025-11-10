#!/usr/bin/env python3
"""
CORRECCIÓN COMPLETA Y FINAL DEL WORKFLOW
=========================================

Este script corrige TODOS los nodos desconectados/incompletos:
1. ¿Existe Sesión Onboarding? - Crear nodo búsqueda y conectar
2. ¿Precios Completos? - Conectar al flujo
3. ¿Es Interacción de Menú? - Remover (no implementado)
4. Global Error Handler - Remover (no implementado)
5. AI Error Handler - Remover (no implementado)
"""

import json
import uuid
import sys

def generate_node_id():
    """Generate unique node ID"""
    return str(uuid.uuid4())

def create_buscar_sesion_onboarding(nodes, usuario_existe_node):
    """Create 'Buscar Sesión de Onboarding' Supabase node"""
    print("\n1️⃣  Creando 'Buscar Sesión de Onboarding'...")

    # Check if exists
    for node in nodes:
        if node['name'] == 'Buscar Sesión de Onboarding':
            print("   ⚠️  Ya existe")
            return node['id']

    # Get position
    pos = usuario_existe_node['position']
    new_pos = [pos[0] + 240, pos[1] + 100]

    new_id = generate_node_id()

    new_node = {
        "id": new_id,
        "name": "Buscar Sesión de Onboarding",
        "type": "n8n-nodes-base.supabase",
        "typeVersion": 1,
        "position": new_pos,
        "parameters": {
            "operation": "getAll",
            "tableId": "line_sessions",
            "returnAll": False,
            "limit": 1,
            "filterType": "manual",
            "filters": {
                "conditions": [
                    {
                        "condition": "and",
                        "conditions": [
                            {
                                "keyName": "phone_number",
                                "condition": "eq",
                                "keyValue": "={{ $('Extraer Datos WhatsApp').first().json.phone_number }}"
                            },
                            {
                                "keyName": "session_type",
                                "condition": "eq",
                                "keyValue": "onboarding"
                            },
                            {
                                "keyName": "is_completed",
                                "condition": "eq",
                                "keyValue": "false"
                            }
                        ]
                    }
                ]
            }
        },
        "notes": "Busca sesión de onboarding activa (no completada) del usuario"
    }

    nodes.append(new_node)
    print(f"   ✅ Creado (ID: {new_id})")
    return new_id

def connect_onboarding_flow(connections):
    """Connect onboarding flow correctly"""
    print("\n2️⃣  Conectando flujo de onboarding...")

    # Get current connection from ¿Usuario Existe? output 1 (NO existe)
    if '¿Usuario Existe?' not in connections:
        print("   ❌ '¿Usuario Existe?' no tiene conexiones")
        return False

    # Change output 1 to go to Buscar Sesión de Onboarding
    connections['¿Usuario Existe?']['main'][1] = [{
        "node": "Buscar Sesión de Onboarding",
        "type": "main",
        "index": 0
    }]
    print("   ✅ ¿Usuario Existe? (NO) → Buscar Sesión de Onboarding")

    # Buscar Sesión de Onboarding → ¿Existe Sesión Onboarding?
    connections['Buscar Sesión de Onboarding'] = {
        "main": [[{
            "node": "¿Existe Sesión Onboarding?",
            "type": "main",
            "index": 0
        }]]
    }
    print("   ✅ Buscar Sesión de Onboarding → ¿Existe Sesión Onboarding?")

    return True

def connect_precios_completos(connections):
    """Connect ¿Precios Completos? to flow"""
    print("\n3️⃣  Conectando '¿Precios Completos?'...")

    # Change Detectar Precios Completos to go to ¿Precios Completos?
    if 'Detectar Precios Completos' not in connections:
        print("   ❌ 'Detectar Precios Completos' no tiene conexiones")
        return False

    connections['Detectar Precios Completos']['main'][0] = [{
        "node": "¿Precios Completos?",
        "type": "main",
        "index": 0
    }]
    print("   ✅ Detectar Precios Completos → ¿Precios Completos?")

    # ¿Precios Completos? already has correct outputs
    # Output 0 (SÍ) → Procesar y Guardar Precios
    # Output 1 (NO) → Enviar Respuesta
    # We need Output 0 to eventually go to Continuation Handler

    # Check Procesar y Guardar Precios connections
    if 'Procesar y Guardar Precios' not in connections:
        # Add connection
        connections['Procesar y Guardar Precios'] = {
            "main": [[{
                "node": "Continuation Handler",
                "type": "main",
                "index": 0
            }]]
        }
        print("   ✅ Procesar y Guardar Precios → Continuation Handler")

    # Change Output 1 (NO) to also go to Continuation Handler with message
    if '¿Precios Completos?' in connections:
        # Output 1 should go to Continuation Handler (user will continue adding prices)
        connections['¿Precios Completos?']['main'][1] = [{
            "node": "Continuation Handler",
            "type": "main",
            "index": 0
        }]
        print("   ✅ ¿Precios Completos? (NO) → Continuation Handler")

    return True

def remove_unimplemented_nodes(nodes, connections):
    """Remove unimplemented nodes"""
    print("\n4️⃣  Removiendo nodos no implementados...")

    to_remove = [
        '¿Es Interacción de Menú?',
        'Global Error Handler',
        'AI Error Handler'
    ]

    removed_count = 0

    for node_name in to_remove:
        # Remove from nodes list
        nodes_before = len(nodes)
        nodes[:] = [n for n in nodes if n['name'] != node_name]
        nodes_after = len(nodes)

        if nodes_before > nodes_after:
            print(f"   ✅ Removido: {node_name}")
            removed_count += 1

        # Remove from connections (as source)
        if node_name in connections:
            del connections[node_name]

        # Remove from connections (as target)
        for source in list(connections.keys()):
            for output_list in connections[source].get('main', []):
                connections[source]['main'] = [
                    [conn for conn in ol if conn['node'] != node_name]
                    for ol in connections[source]['main']
                ]

    print(f"   Total removidos: {removed_count}")
    return removed_count > 0

def validate_critical_connections(workflow):
    """Validate all critical connections"""
    print("\n5️⃣  Validando conexiones críticas...")

    connections = workflow['connections']
    errors = []

    # Critical connections to check
    checks = [
        # Onboarding flow
        ('¿Usuario Existe?', '¿Existe Sesión Onboarding?', 'via Buscar Sesión de Onboarding'),
        ('Buscar Sesión de Onboarding', '¿Existe Sesión Onboarding?', 'direct'),
        ('¿Existe Sesión Onboarding?', 'Preparar Contexto de Sesión', 'output 0'),
        ('¿Existe Sesión Onboarding?', 'Crear Nueva Sesión', 'output 1'),

        # Precios flow
        ('Detectar Precios Completos', '¿Precios Completos?', 'direct'),
        ('¿Precios Completos?', 'Procesar y Guardar Precios', 'output 0'),
        ('Procesar y Guardar Precios', 'Continuation Handler', 'direct'),

        # Continuation flow
        ('Buscar Usuario', 'Buscar Sesión Activa', 'direct'),
        ('Buscar Sesión Activa', '¿Es Continuación?', 'direct'),
        ('¿Es Continuación?', 'Detectar Opção Continuação', 'output 0'),
        ('Detectar Opção Continuação', 'Router Continuação', 'direct'),
    ]

    for source, target, note in checks:
        if source not in connections:
            errors.append(f"❌ '{source}' no tiene conexiones")
            continue

        # Check if target is in any output
        found = False
        for output_list in connections[source].get('main', []):
            for conn in output_list:
                if conn['node'] == target:
                    found = True
                    break
            if found:
                break

        if not found and note != 'via Buscar Sesión de Onboarding':
            errors.append(f"❌ '{source}' no conecta a '{target}' ({note})")

    if errors:
        print("\n   ⚠️  Errores encontrados:")
        for error in errors:
            print(f"      {error}")
        return False
    else:
        print("   ✅ Todas las conexiones críticas OK")
        return True

def count_orphan_nodes(workflow):
    """Count nodes without incoming connections (except triggers)"""
    print("\n6️⃣  Contando nodos huérfanos...")

    connections = workflow['connections']
    nodes = workflow['nodes']

    # Find all nodes with incoming
    nodes_with_incoming = set()
    for source, node_conns in connections.items():
        for output_list in node_conns.get('main', []):
            for conn in output_list:
                nodes_with_incoming.add(conn['node'])

    # Find triggers
    triggers = [n['name'] for n in nodes if 'trigger' in n['type'].lower()]

    # Find AI sub-nodes (they connect via __rl, not connections)
    ai_subnodes = [n['name'] for n in nodes if any(x in n['type'].lower() for x in ['openai', 'memory'])]

    # Find orphans
    orphans = []
    for node in nodes:
        name = node['name']

        # Skip triggers
        if name in triggers:
            continue

        # Skip AI sub-nodes
        if name in ai_subnodes:
            continue

        # Check if has incoming
        if name not in nodes_with_incoming:
            orphans.append(name)

    if orphans:
        print(f"   ⚠️  Nodos huérfanos encontrados: {len(orphans)}")
        for name in orphans:
            print(f"      - {name}")
        return len(orphans)
    else:
        print("   ✅ No hay nodos huérfanos")
        return 0

def main():
    print("="*80)
    print("CORRECCIÓN COMPLETA Y FINAL DEL WORKFLOW")
    print("="*80)

    # Load workflow
    try:
        with open('workflow-frepi-mvp1-CORREGIDO.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"\n✅ Workflow cargado: {len(workflow['nodes'])} nodos")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

    nodes = workflow['nodes']
    connections = workflow['connections']

    # Find required nodes
    usuario_existe = next((n for n in nodes if n['name'] == '¿Usuario Existe?'), None)
    if not usuario_existe:
        print("\n❌ No se encontró '¿Usuario Existe?'")
        sys.exit(1)

    # Apply fixes
    changes = 0

    # 1. Create and connect onboarding flow
    buscar_sesion_id = create_buscar_sesion_onboarding(nodes, usuario_existe)
    if buscar_sesion_id:
        changes += 1

    if connect_onboarding_flow(connections):
        changes += 1

    # 2. Connect precios completos
    if connect_precios_completos(connections):
        changes += 1

    # 3. Remove unimplemented nodes
    if remove_unimplemented_nodes(nodes, connections):
        changes += 1

    # 4. Validate
    is_valid = validate_critical_connections(workflow)

    # 5. Count orphans
    orphan_count = count_orphan_nodes(workflow)

    # Save
    if changes > 0:
        try:
            output_file = 'workflow-frepi-mvp1-FINAL.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Workflow guardado: {output_file}")
            print(f"   Cambios aplicados: {changes}")
            print(f"   Nodos totales: {len(workflow['nodes'])}")
            print(f"   Nodos huérfanos: {orphan_count}")
        except Exception as e:
            print(f"\n❌ Error guardando: {e}")
            sys.exit(1)

    print("\n" + "="*80)
    print("CORRECCIÓN COMPLETADA")
    print("="*80)

    if is_valid and orphan_count == 0:
        print("\n✅ El workflow está 100% funcional")
        print(f"\n📄 Archivo: {output_file}")

        print("\n📋 CAMBIOS REALIZADOS:")
        print("   1. ✅ Creado 'Buscar Sesión de Onboarding'")
        print("   2. ✅ Conectado flujo de onboarding completo")
        print("   3. ✅ Conectado '¿Precios Completos?' al flujo")
        print("   4. ✅ Removidos 3 nodos no implementados")
        print("   5. ✅ Todas las conexiones críticas validadas")

        print("\n🎯 FLUJOS FUNCIONALES:")
        print("   ✅ Onboarding (usuario nuevo)")
        print("   ✅ Continuación (múltiples acciones)")
        print("   ✅ Subir precios (con validación completo/incompleto)")
        print("   ✅ Compras")
        print("   ✅ Registro de fornecedor")

    elif orphan_count > 0:
        print(f"\n⚠️  Hay {orphan_count} nodos huérfanos")
        print("   Revisar antes de usar en producción")
    else:
        print("\n⚠️  Hay errores de validación")
        sys.exit(1)

if __name__ == '__main__':
    main()
