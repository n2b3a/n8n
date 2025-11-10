#!/usr/bin/env python3
"""
CORRECCIÓN COMPLETA DEL FLUJO DE CONTINUACIÓN

Este script corrige el workflow para que el flujo de continuación funcione correctamente.
"""

import json
import uuid
import sys

def generate_node_id():
    """Generate unique node ID"""
    return str(uuid.uuid4())

def modify_update_session_db(nodes):
    """Add awaiting_continuation field to Update Session DB"""
    print("\n1️⃣ Modificando 'Update Session DB'...")

    for node in nodes:
        if node['name'] == 'Update Session DB':
            # Check if already has awaiting_continuation
            fields = node['parameters']['fieldsUi']['fieldValues']
            has_field = any(f['fieldId'] == 'awaiting_continuation' for f in fields)

            if has_field:
                print("   ⚠️  Ya tiene campo awaiting_continuation - skipping")
                return False

            # Add awaiting_continuation field
            fields.append({
                'fieldId': 'awaiting_continuation',
                'fieldValue': '={{ $json.awaiting_continuation || false }}'
            })

            print("   ✅ Agregado campo 'awaiting_continuation' a Update Session DB")
            return True

    print("   ❌ Nodo 'Update Session DB' no encontrado")
    return False

def create_buscar_sesion_node(nodes, buscar_usuario_node):
    """Create 'Buscar Sesión Activa' Supabase node"""
    print("\n2️⃣ Creando nodo 'Buscar Sesión Activa'...")

    # Check if already exists
    for node in nodes:
        if node['name'] == 'Buscar Sesión Activa':
            print("   ⚠️  Nodo ya existe - skipping")
            return node['id']

    # Get position
    buscar_pos = buscar_usuario_node['position']
    new_pos = [buscar_pos[0] + 240, buscar_pos[1]]

    new_node_id = generate_node_id()

    new_node = {
        "id": new_node_id,
        "name": "Buscar Sesión Activa",
        "type": "n8n-nodes-base.supabase",
        "typeVersion": 1,
        "position": new_pos,
        "parameters": {
            "operation": "get",
            "tableId": "line_sessions",
            "filterType": "manual",
            "matchMode": "equals",
            "filterBy": "={{ $('Buscar Usuario').first().json.id }}",
            "filterColumn": "user_id",
            "returnFields": "id, user_id, awaiting_continuation, continuation_timestamp, session_type, is_completed"
        },
        "notes": "Busca la sesión activa del usuario para verificar awaiting_continuation"
    }

    nodes.append(new_node)
    print(f"   ✅ Creado nodo 'Buscar Sesión Activa' (ID: {new_node_id})")
    return new_node_id

def create_es_continuacion_node(nodes, buscar_sesion_node):
    """Create '¿Es Continuación?' IF node"""
    print("\n3️⃣ Creando nodo '¿Es Continuación?'...")

    # Check if already exists
    for node in nodes:
        if node['name'] == '¿Es Continuación?':
            print("   ⚠️  Nodo ya existe - skipping")
            return node['id']

    # Get position from Buscar Sesión
    buscar_sesion_node_obj = next(n for n in nodes if n['id'] == buscar_sesion_node)
    buscar_pos = buscar_sesion_node_obj['position']
    new_pos = [buscar_pos[0] + 240, buscar_pos[1]]

    new_node_id = generate_node_id()

    new_node = {
        "id": new_node_id,
        "name": "¿Es Continuación?",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": new_pos,
        "parameters": {
            "conditions": {
                "options": {
                    "caseSensitive": True,
                    "leftValue": "",
                    "typeValidation": "strict",
                    "version": 2
                },
                "conditions": [
                    {
                        "id": "CONTINUATION_CHECK",
                        "leftValue": "={{ $('Buscar Sesión Activa').first().json.awaiting_continuation }}",
                        "rightValue": "",
                        "operator": {
                            "type": "boolean",
                            "operation": "true",
                            "singleValue": True
                        }
                    }
                ],
                "combinator": "and"
            }
        },
        "notes": "Verifica si el usuario está esperando responder a mensaje de continuación"
    }

    nodes.append(new_node)
    print(f"   ✅ Creado nodo '¿Es Continuación?' (ID: {new_node_id})")
    return new_node_id

def modify_detectar_opcao(nodes):
    """Modify Detectar Opção Continuação to reset awaiting_continuation"""
    print("\n4️⃣ Modificando 'Detectar Opção Continuação'...")

    for node in nodes:
        if node['name'] == 'Detectar Opção Continuação':
            code = node['parameters']['jsCode']

            # Check if already has reset code
            if 'awaiting_continuation: false' in code and 'await $supabase' in code and 'awaiting_continuation' in code:
                print("   ⚠️  Ya tiene código de reset - skipping")
                return False

            # Find the return statement
            lines = code.split('\n')
            return_index = -1
            for i in range(len(lines) - 1, -1, -1):
                if 'return [{' in lines[i]:
                    return_index = i
                    break

            if return_index > 0:
                # Insert UPDATE before return
                reset_code = """
  // 🔄 Resetear flag de continuación en la base de datos
  await $supabase
    .from('line_sessions')
    .update({ awaiting_continuation: false })
    .eq('user_id', usuario.user_id);

  console.log('✅ [Detectar Continuação] Reset awaiting_continuation = false');
"""
                lines.insert(return_index, reset_code)

                # Also add field to return json
                for i in range(return_index, len(lines)):
                    if 'output_route' in lines[i]:
                        lines[i] = lines[i].rstrip(',') + ','
                        indent = '    '
                        lines.insert(i + 1, f'{indent}awaiting_continuation: false')
                        break

                node['parameters']['jsCode'] = '\n'.join(lines)
                print("   ✅ Agregado código para resetear awaiting_continuation")
                return True

    print("   ❌ Nodo 'Detectar Opção Continuação' no encontrado")
    return False

def update_connections(workflow, buscar_sesion_id, es_continuacion_id):
    """Update all connections"""
    print("\n5️⃣ Actualizando conexiones...")

    connections = workflow['connections']

    # 1. Buscar Usuario → Buscar Sesión Activa
    if 'Buscar Usuario' not in connections:
        print("   ❌ 'Buscar Usuario' no tiene conexiones")
        return False

    original_target = connections['Buscar Usuario']['main'][0][0]['node']

    connections['Buscar Usuario']['main'][0] = [{
        "node": "Buscar Sesión Activa",
        "type": "main",
        "index": 0
    }]
    print("   ✅ Conectado: Buscar Usuario → Buscar Sesión Activa")

    # 2. Buscar Sesión Activa → ¿Es Continuación?
    connections['Buscar Sesión Activa'] = {
        "main": [[{
            "node": "¿Es Continuación?",
            "type": "main",
            "index": 0
        }]]
    }
    print("   ✅ Conectado: Buscar Sesión Activa → ¿Es Continuación?")

    # 3. ¿Es Continuación? → outputs
    connections['¿Es Continuación?'] = {
        "main": [
            [{
                "node": "Detectar Opção Continuação",
                "type": "main",
                "index": 0
            }],
            [{
                "node": original_target,
                "type": "main",
                "index": 0
            }]
        ]
    }
    print(f"   ✅ Conectado: ¿Es Continuación? (true) → Detectar Opção Continuação")
    print(f"   ✅ Conectado: ¿Es Continuación? (false) → {original_target}")

    return True

def validate_workflow(workflow):
    """Validate workflow"""
    print("\n6️⃣ Validando workflow...")

    connections = workflow['connections']
    errors = []

    # Check Update Session DB has awaiting_continuation field
    for node in workflow['nodes']:
        if node['name'] == 'Update Session DB':
            fields = node['parameters']['fieldsUi']['fieldValues']
            has_field = any(f['fieldId'] == 'awaiting_continuation' for f in fields)
            if not has_field:
                errors.append("❌ Update Session DB no tiene campo awaiting_continuation")

    # Check connections
    checks = [
        ('Buscar Usuario', 'Buscar Sesión Activa'),
        ('Buscar Sesión Activa', '¿Es Continuación?'),
        ('Detectar Opção Continuação', 'Router Continuação'),
    ]

    for source, target in checks:
        if source not in connections:
            errors.append(f"❌ '{source}' no tiene conexiones")
        else:
            actual_target = connections[source]['main'][0][0]['node']
            if actual_target != target:
                errors.append(f"❌ '{source}' conecta a '{actual_target}' en vez de '{target}'")

    # Check ¿Es Continuación? has 2 outputs
    if '¿Es Continuación?' not in connections:
        errors.append("❌ '¿Es Continuación?' no tiene conexiones")
    else:
        outputs = connections['¿Es Continuación?']['main']
        if len(outputs) != 2:
            errors.append(f"❌ '¿Es Continuación?' tiene {len(outputs)} outputs en vez de 2")

    if errors:
        print("\n⚠️  ERRORES:")
        for error in errors:
            print(f"   {error}")
        return False
    else:
        print("   ✅ Todas las validaciones pasaron")
        return True

def create_flow_diagram():
    """Create visual flow diagram"""
    diagram = """
╔════════════════════════════════════════════════════════════════════════════════╗
║                     FLUJO DE CONTINUACIÓN CORREGIDO                            ║
╚════════════════════════════════════════════════════════════════════════════════╝

📱 ESCENARIO 1: Usuario completa una acción
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Usuario completa compra/precios/fornecedor
              ↓
    Continuation Handler
              ↓ (pone awaiting_continuation: true en JSON)
    Update Session DB
              ↓ (guarda awaiting_continuation: true en line_sessions)
    Enviar Respuesta
              ↓
    "✅ Pronto! 💬 Posso te ajudar com algo mais?
     1️⃣ Fazer outra compra
     2️⃣ Atualizar preços
     3️⃣ Registrar fornecedor
     4️⃣ Ver menú principal"


📱 ESCENARIO 2: Usuario responde "1"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Usuario envía "1"
              ↓
    WhatsApp Trigger → Config Global → Extraer Datos
              ↓
    ¿Archivo No Soportado? (NO)
              ↓
    Buscar Usuario (restaurant_people)
              ↓
    Buscar Sesión Activa (line_sessions) ← ✨ NUEVO
              ↓ (trae awaiting_continuation: true)
    ¿Es Continuación? ← ✨ NUEVO
              ↓ (SÍ - awaiting_continuation = true)
    Detectar Opção Continuação ← ✨ AHORA SE EJECUTA
              ↓ (procesa "1" = hacer compra, resetea flag)
    Router Continuação
              ↓ (output 0)
    Crear Sesión de Compra
              ↓
    ... flujo de compra ...
              ↓
    ✅ FUNCIONA!


📱 ESCENARIO 3: Usuario envía mensaje normal (no es continuación)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Usuario envía "menu" o cualquier mensaje
              ↓
    ... (mismo flujo inicial) ...
              ↓
    Buscar Sesión Activa (line_sessions)
              ↓ (awaiting_continuation: false o null)
    ¿Es Continuación?
              ↓ (NO - awaiting_continuation = false)
    ¿Usuario Existe? ← Flujo normal continúa
              ↓
    ... (flujo normal) ...


╔════════════════════════════════════════════════════════════════════════════════╗
║                     CAMBIOS REALIZADOS                                         ║
╚════════════════════════════════════════════════════════════════════════════════╝

✅ 1. Update Session DB
   - Agregado campo: awaiting_continuation

✅ 2. Buscar Sesión Activa (NUEVO NODO)
   - Tipo: Supabase
   - Tabla: line_sessions
   - Trae: awaiting_continuation, user_id, session_type, etc.

✅ 3. ¿Es Continuación? (NUEVO NODO)
   - Tipo: IF
   - Condición: $('Buscar Sesión Activa').first().json.awaiting_continuation === true

✅ 4. Detectar Opção Continuação
   - Agregado: UPDATE para resetear awaiting_continuation = false

✅ 5. Conexiones actualizadas:
   - Buscar Usuario → Buscar Sesión Activa → ¿Es Continuación?
   - ¿Es Continuación? (true) → Detectar Opção Continuação
   - ¿Es Continuación? (false) → ¿Usuario Existe? (flujo normal)
"""
    return diagram

def main():
    print("="*80)
    print("CORRECCIÓN COMPLETA DEL FLUJO DE CONTINUACIÓN")
    print("="*80)

    # Load workflow
    try:
        with open('workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"\n✅ Workflow cargado: {len(workflow['nodes'])} nodos")
    except Exception as e:
        print(f"\n❌ Error cargando workflow: {e}")
        sys.exit(1)

    nodes = workflow['nodes']

    # Find required nodes
    buscar_usuario_node = next((n for n in nodes if n['name'] == 'Buscar Usuario'), None)
    if not buscar_usuario_node:
        print("\n❌ No se encontró 'Buscar Usuario'")
        sys.exit(1)

    # Apply fixes
    changes = 0

    if modify_update_session_db(nodes):
        changes += 1

    buscar_sesion_id = create_buscar_sesion_node(nodes, buscar_usuario_node)
    if buscar_sesion_id:
        changes += 1

    es_continuacion_id = create_es_continuacion_node(nodes, buscar_sesion_id)
    if es_continuacion_id:
        changes += 1

    if modify_detectar_opcao(nodes):
        changes += 1

    if update_connections(workflow, buscar_sesion_id, es_continuacion_id):
        changes += 1

    # Validate
    is_valid = validate_workflow(workflow)

    if changes > 0:
        # Save corrected workflow
        try:
            output_file = 'workflow-frepi-mvp1-CORREGIDO.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Workflow corregido guardado: {output_file}")
            print(f"   Total de cambios: {changes}")
            print(f"   Total de nodos: {len(workflow['nodes'])}")
        except Exception as e:
            print(f"\n❌ Error guardando: {e}")
            sys.exit(1)

    # Show diagram
    print("\n" + "="*80)
    print("CORRECCIÓN COMPLETADA")
    print("="*80)

    if is_valid:
        print("\n✅ El workflow está listo para importar en n8n")
        print(f"\n📄 Archivo: workflow-frepi-mvp1-CORREGIDO.json")
        print("\n" + create_flow_diagram())
    else:
        print("\n⚠️  Hay errores - revisar antes de importar")
        sys.exit(1)

if __name__ == '__main__':
    main()
