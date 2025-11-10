#!/usr/bin/env python3
"""
FIX: Corregir flujo de continuación del workflow Frepi MVP

PROBLEMAS A CORREGIR:
1. "Continuation Handler" no marca awaiting_continuation = true
2. "Buscar Usuario" no incluye campo awaiting_continuation
3. No existe nodo "¿Es Continuación?" para rutear el flujo
4. "Detectar Opção Continuação" está desconectado
5. Flujo roto: Usuario no puede hacer segunda acción

SOLUCIÓN:
- Agregar marcador awaiting_continuation en Continuation Handler
- Incluir campo en Buscar Usuario
- Crear nodo IF "¿Es Continuación?"
- Conectar todo el flujo correctamente
"""

import json
import uuid
import sys

def generate_node_id():
    """Generate unique node ID"""
    return str(uuid.uuid4())

def modify_continuation_handler(nodes):
    """Modify Continuation Handler to mark awaiting_continuation = true"""
    print("\n1️⃣ Modificando 'Continuation Handler'...")

    for node in nodes:
        if node['name'] == 'Continuation Handler':
            code = node['parameters']['jsCode']

            # Buscar donde retorna y agregar UPDATE antes
            if 'await $supabase' not in code or 'awaiting_continuation' in code:
                if 'awaiting_continuation' in code:
                    print("   ⚠️  Ya tiene awaiting_continuation - skipping")
                    return False

            # Agregar el UPDATE antes del return
            # Buscar el return final
            lines = code.split('\n')
            return_index = -1
            for i in range(len(lines) - 1, -1, -1):
                if 'return [{' in lines[i]:
                    return_index = i
                    break

            if return_index > 0:
                # Insertar el UPDATE antes del return
                update_code = """
  // 🔄 Marcar que el usuario está esperando respuesta de continuación
  await $supabase
    .from('sessions')
    .update({
      awaiting_continuation: true,
      continuation_timestamp: new Date().toISOString()
    })
    .eq('phone_number', usuario.phone_number);

  console.log('✅ [Continuation] Marcado awaiting_continuation = true');
"""
                lines.insert(return_index, update_code)
                node['parameters']['jsCode'] = '\n'.join(lines)
                print("   ✅ Agregado: await $supabase.update awaiting_continuation = true")
                return True

    print("   ❌ Nodo 'Continuation Handler' no encontrado")
    return False

def modify_buscar_usuario(nodes):
    """Modify Buscar Usuario to include awaiting_continuation field"""
    print("\n2️⃣ Modificando 'Buscar Usuario'...")

    for node in nodes:
        if node['name'] == 'Buscar Usuario':
            code = node['parameters']['jsCode']

            # Verificar si ya tiene awaiting_continuation
            if 'awaiting_continuation' in code:
                print("   ⚠️  Ya incluye awaiting_continuation - skipping")
                return False

            # Buscar el .select() y agregar el campo
            if ".select('*')" in code:
                code = code.replace(".select('*')", ".select('*, awaiting_continuation')")
                node['parameters']['jsCode'] = code
                print("   ✅ Agregado campo 'awaiting_continuation' al SELECT")
                return True
            elif ".select(" in code:
                # Buscar la línea del select
                lines = code.split('\n')
                for i, line in enumerate(lines):
                    if '.select(' in line:
                        # Verificar si ya tiene awaiting_continuation
                        if 'awaiting_continuation' not in line:
                            # Agregar al final de la selección
                            if line.strip().endswith(')'):
                                lines[i] = line.replace(')', ', awaiting_continuation)')
                            else:
                                # Buscar el cierre del select
                                for j in range(i + 1, len(lines)):
                                    if ')' in lines[j]:
                                        lines[j] = lines[j].replace(')', ', awaiting_continuation)')
                                        break

                            node['parameters']['jsCode'] = '\n'.join(lines)
                            print("   ✅ Agregado campo 'awaiting_continuation' al SELECT")
                            return True

    print("   ❌ Nodo 'Buscar Usuario' no encontrado")
    return False

def create_es_continuacion_node(nodes, buscar_usuario_node):
    """Create '¿Es Continuación?' IF node"""
    print("\n3️⃣ Creando nodo '¿Es Continuación?'...")

    # Check if already exists
    for node in nodes:
        if node['name'] == '¿Es Continuación?':
            print("   ⚠️  Nodo ya existe - skipping")
            return node['id']

    # Get position from Buscar Usuario
    buscar_pos = buscar_usuario_node['position']
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
                        "leftValue": "={{ $json.awaiting_continuation }}",
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
    """Modify Detectar Opção Continuação to reset awaiting_continuation flag"""
    print("\n4️⃣ Modificando 'Detectar Opção Continuação'...")

    for node in nodes:
        if node['name'] == 'Detectar Opção Continuação':
            code = node['parameters']['jsCode']

            # Verificar si ya resetea el flag
            if 'awaiting_continuation: false' in code:
                print("   ⚠️  Ya resetea awaiting_continuation - skipping")
                return False

            # Buscar el return final y agregar el reset antes
            lines = code.split('\n')
            return_index = -1
            for i in range(len(lines) - 1, -1, -1):
                if 'return [{' in lines[i]:
                    return_index = i
                    break

            if return_index > 0:
                reset_code = """
  // 🔄 Resetear flag de continuación
  await $supabase
    .from('sessions')
    .update({ awaiting_continuation: false })
    .eq('phone_number', usuario.phone_number);

  console.log('✅ [Detectar Continuação] Reset awaiting_continuation = false');
"""
                lines.insert(return_index, reset_code)

                # También agregar el campo en el json de retorno
                # Buscar json: { dentro del return
                for i in range(return_index, len(lines)):
                    if 'json: {' in lines[i]:
                        # Buscar el final del objeto json
                        for j in range(i + 1, len(lines)):
                            if 'output_route' in lines[j]:
                                # Agregar después de output_route
                                indent = '    '
                                lines[j] = lines[j].rstrip(',') + ','
                                lines.insert(j + 1, f'{indent}awaiting_continuation: false')
                                break
                        break

                node['parameters']['jsCode'] = '\n'.join(lines)
                print("   ✅ Agregado: Reset awaiting_continuation = false")
                return True

    print("   ❌ Nodo 'Detectar Opção Continuação' no encontrado")
    return False

def update_connections(workflow, es_continuacion_id):
    """Update connections to include new node in flow"""
    print("\n5️⃣ Actualizando conexiones...")

    connections = workflow['connections']

    # Buscar "Buscar Usuario" en connections
    if 'Buscar Usuario' not in connections:
        print("   ❌ 'Buscar Usuario' no tiene conexiones")
        return False

    # Guardar la conexión actual de Buscar Usuario
    buscar_current = connections['Buscar Usuario']['main'][0][0]
    original_target = buscar_current['node']

    # Conectar Buscar Usuario → ¿Es Continuación?
    connections['Buscar Usuario']['main'][0] = [{
        "node": "¿Es Continuación?",
        "type": "main",
        "index": 0
    }]
    print(f"   ✅ Conectado: Buscar Usuario → ¿Es Continuación?")

    # Conectar ¿Es Continuación? → outputs
    connections['¿Es Continuación?'] = {
        "main": [
            [
                {
                    "node": "Detectar Opção Continuação",
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
    print(f"   ✅ Conectado: ¿Es Continuación? (true) → Detectar Opção Continuação")
    print(f"   ✅ Conectado: ¿Es Continuación? (false) → {original_target}")

    return True

def validate_workflow(workflow):
    """Validate that all critical connections are in place"""
    print("\n6️⃣ Validando workflow corregido...")

    connections = workflow['connections']
    errors = []

    # 1. Verificar Continuation Handler → Update Session DB
    if 'Continuation Handler' not in connections:
        errors.append("❌ 'Continuation Handler' no tiene conexiones")
    else:
        target = connections['Continuation Handler']['main'][0][0]['node']
        if target != 'Update Session DB':
            errors.append(f"❌ 'Continuation Handler' conecta a '{target}' en vez de 'Update Session DB'")

    # 2. Verificar Buscar Usuario → ¿Es Continuación?
    if 'Buscar Usuario' not in connections:
        errors.append("❌ 'Buscar Usuario' no tiene conexiones")
    else:
        target = connections['Buscar Usuario']['main'][0][0]['node']
        if target != '¿Es Continuación?':
            errors.append(f"❌ 'Buscar Usuario' conecta a '{target}' en vez de '¿Es Continuación?'")

    # 3. Verificar ¿Es Continuación? tiene 2 outputs
    if '¿Es Continuación?' not in connections:
        errors.append("❌ '¿Es Continuación?' no tiene conexiones")
    else:
        outputs = connections['¿Es Continuación?']['main']
        if len(outputs) != 2:
            errors.append(f"❌ '¿Es Continuación?' tiene {len(outputs)} outputs en vez de 2")
        else:
            # Output 0 (true) debe ir a Detectar Opção Continuação
            if outputs[0][0]['node'] != 'Detectar Opção Continuação':
                errors.append(f"❌ '¿Es Continuación?' output 0 conecta a '{outputs[0][0]['node']}'")

    # 4. Verificar Detectar Opção Continuação → Router Continuação
    if 'Detectar Opção Continuação' not in connections:
        errors.append("❌ 'Detectar Opção Continuação' no tiene conexiones")
    else:
        target = connections['Detectar Opção Continuação']['main'][0][0]['node']
        if target != 'Router Continuação':
            errors.append(f"❌ 'Detectar Opção Continuação' conecta a '{target}' en vez de 'Router Continuação'")

    if errors:
        print("\n⚠️  ERRORES DE VALIDACIÓN:")
        for error in errors:
            print(f"   {error}")
        return False
    else:
        print("   ✅ Todas las conexiones críticas están correctas")
        return True

def main():
    print("="*80)
    print("CORRECCIÓN DEL FLUJO DE CONTINUACIÓN")
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

    # Find Buscar Usuario node
    buscar_usuario_node = next((n for n in nodes if n['name'] == 'Buscar Usuario'), None)
    if not buscar_usuario_node:
        print("\n❌ No se encontró nodo 'Buscar Usuario'")
        sys.exit(1)

    # Apply fixes
    changes = 0

    if modify_continuation_handler(nodes):
        changes += 1

    if modify_buscar_usuario(nodes):
        changes += 1

    es_continuacion_id = create_es_continuacion_node(nodes, buscar_usuario_node)
    if es_continuacion_id:
        changes += 1

    if modify_detectar_opcao(nodes):
        changes += 1

    if update_connections(workflow, es_continuacion_id):
        changes += 1

    # Validate
    is_valid = validate_workflow(workflow)

    if changes > 0:
        # Save corrected workflow
        try:
            with open('workflow-frepi-mvp1-mejorado-CORREGIDO.json', 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Workflow corregido guardado: workflow-frepi-mvp1-mejorado-CORREGIDO.json")
            print(f"   Total de cambios aplicados: {changes}")
        except Exception as e:
            print(f"\n❌ Error guardando workflow: {e}")
            sys.exit(1)

    print("\n" + "="*80)
    print("CORRECCIÓN COMPLETADA")
    print("="*80)

    if is_valid:
        print("\n✅ El workflow está listo para importar en n8n")
        print("\n📋 FLUJO CORREGIDO:")
        print("   Usuario completa acción")
        print("   ↓")
        print("   Continuation Handler (marca awaiting_continuation = true)")
        print("   ↓")
        print("   Update Session DB → Enviar mensaje con opciones")
        print("   ↓")
        print("   Usuario responde '1'")
        print("   ↓")
        print("   WhatsApp Trigger → Extraer Datos → Buscar Usuario")
        print("   ↓")
        print("   ¿Es Continuación? (SÍ - awaiting_continuation = true)")
        print("   ↓")
        print("   Detectar Opção Continuação (procesa '1', resetea flag)")
        print("   ↓")
        print("   Router Continuação (output 0)")
        print("   ↓")
        print("   Crear Sesión de Compra")
        print("   ✅ FUNCIONA!")
    else:
        print("\n⚠️  Hay errores de validación - revisar antes de importar")
        sys.exit(1)

if __name__ == '__main__':
    main()
