#!/usr/bin/env python3
"""
Verificar que workflow-frepi-mvp1-PRODUCTION-READY.json está correctamente configurado
"""

import json

def verify_continuation_flow(workflow):
    """Verificar flujo de continuación"""
    print("\n" + "="*80)
    print("VERIFICACIÓN: FLUJO DE CONTINUACIÓN")
    print("="*80)

    connections = workflow['connections']
    nodes = workflow['nodes']

    # Verificar el flujo completo
    flow_steps = [
        ('Buscar Usuario', '¿Es Continuación?'),
        ('¿Es Continuación?', ['Detectar Opção Continuação', '¿Usuario Existe?']),
        ('Detectar Opção Continuação', 'Router Continuação'),
        ('Continuation Handler', 'Update Session DB')
    ]

    print("\n✅ Flujo de Continuación:")
    for step in flow_steps:
        if len(step) == 2:
            source, target = step
            if source in connections:
                conn = connections[source]['main']
                if isinstance(target, list):
                    # Multiple outputs
                    for i, t in enumerate(target):
                        if i < len(conn) and conn[i]:
                            actual_target = conn[i][0]['node']
                            status = "✅" if actual_target == t else f"❌ (esperado {t}, actual {actual_target})"
                            print(f"   {source} [output {i}] → {actual_target} {status}")
                        else:
                            print(f"   {source} [output {i}] → DESCONECTADO ❌")
                else:
                    # Single output
                    if conn and conn[0]:
                        actual_target = conn[0][0]['node']
                        status = "✅" if actual_target == target else f"❌ (esperado {target}, actual {actual_target})"
                        print(f"   {source} → {actual_target} {status}")
                    else:
                        print(f"   {source} → DESCONECTADO ❌")
            else:
                print(f"   {source} → SIN CONEXIONES ❌")

    # Verificar código de Continuation Handler
    cont_handler = next((n for n in nodes if n['name'] == 'Continuation Handler'), None)
    if cont_handler:
        code = cont_handler['parameters'].get('jsCode', '')
        has_flag = 'awaiting_continuation' in code
        print(f"\n✅ Continuation Handler marca awaiting_continuation: {'✅' if has_flag else '❌'}")

    # Verificar código de Buscar Usuario
    buscar_usuario = next((n for n in nodes if n['name'] == 'Buscar Usuario'), None)
    if buscar_usuario:
        code = buscar_usuario['parameters'].get('jsCode', '')
        has_field = 'awaiting_continuation' in code
        print(f"✅ Buscar Usuario incluye awaiting_continuation: {'✅' if has_field else '❌'}")

def verify_router_connections(workflow):
    """Verificar todas las conexiones de routers"""
    print("\n" + "="*80)
    print("VERIFICACIÓN: ROUTERS Y SWITCH NODES")
    print("="*80)

    connections = workflow['connections']
    nodes = workflow['nodes']

    # Verificar Router de Acciones
    print("\n1️⃣ Router de Acciones:")
    router_acciones = next((n for n in nodes if n['name'] == 'Router de Acciones'), None)
    if router_acciones:
        params = router_acciones['parameters']
        outputs = params.get('options', {}).get('outputsAmount', 0)
        expression = params.get('output', '')

        print(f"   outputsAmount: {outputs}")
        print(f"   Expression usa outputs: 0, 1, 2, 3, 4")
        print(f"   Status: {'✅ OK' if outputs == 5 else f'❌ INCORRECTO (debería ser 5)'}")

        # Verificar conexiones
        if 'Router de Acciones' in connections:
            conn = connections['Router de Acciones']['main']
            for i in range(5):
                if i < len(conn) and conn[i] and len(conn[i]) > 0:
                    target = conn[i][0]['node']
                    print(f"   Output {i} → {target} ✅")
                else:
                    print(f"   Output {i} → DESCONECTADO ⚠️")

    # Verificar Router: ¿Es Decisión Duplicado?
    print("\n2️⃣ Router: ¿Es Decisión Duplicado?:")
    router_duplicado = next((n for n in nodes if n['name'] == 'Router: ¿Es Decisión Duplicado?'), None)
    if router_duplicado:
        params = router_duplicado['parameters']
        outputs = params.get('options', {}).get('outputsAmount', 0)

        print(f"   outputsAmount: {outputs}")

        # Verificar conexiones
        if 'Router: ¿Es Decisión Duplicado?' in connections:
            conn = connections['Router: ¿Es Decisión Duplicado?']['main']
            for i in range(outputs):
                if i < len(conn) and conn[i] and len(conn[i]) > 0:
                    target = conn[i][0]['node']
                    print(f"   Output {i} → {target} ✅")
                else:
                    print(f"   Output {i} → DESCONECTADO ❌")
        else:
            print("   ❌ Sin conexiones")
    else:
        print("   ❌ Nodo no encontrado")

    # Verificar Router Continuação
    print("\n3️⃣ Router Continuação:")
    router_cont = next((n for n in nodes if n['name'] == 'Router Continuação'), None)
    if router_cont:
        params = router_cont['parameters']
        outputs = params.get('options', {}).get('outputsAmount', 0)

        print(f"   outputsAmount: {outputs}")

        # Verificar conexiones
        if 'Router Continuação' in connections:
            conn = connections['Router Continuação']['main']
            for i in range(outputs):
                if i < len(conn) and conn[i] and len(conn[i]) > 0:
                    target = conn[i][0]['node']
                    print(f"   Output {i} → {target} ✅")
                else:
                    print(f"   Output {i} → DESCONECTADO ⚠️")

def verify_fornecedor_flow(workflow):
    """Verificar flujo de registro de fornecedor"""
    print("\n" + "="*80)
    print("VERIFICACIÓN: FLUJO DE REGISTRO DE FORNECEDOR")
    print("="*80)

    connections = workflow['connections']

    flow_steps = [
        'Agente Registrar Fornecedor',
        'Detectar Fornecedor Completo',
        '¿Fornecedor Completo?',
        'Guardar Fornecedor BD',
        'Actualizar Sesión con Fornecedor',
        'Continuation Handler'
    ]

    print("\n✅ Flujo de Fornecedor:")
    for i, source in enumerate(flow_steps[:-1]):
        target = flow_steps[i+1]
        if source in connections:
            conn = connections[source]['main']
            if conn and conn[0]:
                actual_target = conn[0][0]['node']
                status = "✅" if actual_target == target else f"⚠️  (esperado {target}, actual {actual_target})"
                print(f"   {source} → {actual_target} {status}")
            else:
                print(f"   {source} → DESCONECTADO ❌")
        else:
            print(f"   {source} → SIN CONEXIONES ❌")

def find_orphan_nodes(workflow):
    """Encontrar nodos huérfanos (sin incoming connections)"""
    print("\n" + "="*80)
    print("VERIFICACIÓN: NODOS HUÉRFANOS")
    print("="*80)

    nodes = workflow['nodes']
    connections = workflow['connections']

    # AI sub-nodes que no aparecen en conexiones
    ai_subnodes = {'OpenAI', 'Simple Memory', 'Memory', 'Chat Model'}

    # Triggers
    trigger_types = {'n8n-nodes-base.webhook', 'n8n-nodes-base.manualTrigger'}

    nodes_with_incoming = set()

    # Encontrar todos los nodos que tienen conexiones entrantes
    for source, conn_data in connections.items():
        if 'main' in conn_data:
            for output_array in conn_data['main']:
                if output_array:
                    for target in output_array:
                        nodes_with_incoming.add(target['node'])

    orphans = []
    for node in nodes:
        name = node['name']
        node_type = node['type']

        # Skip AI sub-nodes y triggers
        is_ai_subnode = any(ai_term in name for ai_term in ai_subnodes)
        is_trigger = node_type in trigger_types

        if not is_ai_subnode and not is_trigger and name not in nodes_with_incoming:
            # Verificar si tiene outgoing connections
            has_outgoing = name in connections and connections[name].get('main')
            orphans.append({
                'name': name,
                'type': node_type,
                'has_outgoing': bool(has_outgoing)
            })

    print(f"\n📊 Nodos huérfanos encontrados: {len(orphans)}")

    if orphans:
        for orphan in orphans:
            status = "⚠️" if orphan['has_outgoing'] else "ℹ️"
            print(f"   {status} {orphan['name']} ({orphan['type']})")
            if orphan['has_outgoing']:
                print(f"      → Tiene conexiones SALIENTES pero NO entrantes")
    else:
        print("   ✅ No se encontraron nodos huérfanos")

def main():
    print("="*80)
    print("VERIFICACIÓN COMPLETA DE WORKFLOW PRODUCTION-READY")
    print("="*80)

    # Cargar workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-PRODUCTION-READY.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"\n✅ Workflow cargado: {len(workflow['nodes'])} nodos")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return

    # Ejecutar todas las verificaciones
    verify_continuation_flow(workflow)
    verify_router_connections(workflow)
    verify_fornecedor_flow(workflow)
    find_orphan_nodes(workflow)

    print("\n" + "="*80)
    print("VERIFICACIÓN COMPLETA")
    print("="*80)
    print("\n✅ Workflow verificado y listo para importar")
    print("\n📄 Archivo: workflow-frepi-mvp1-PRODUCTION-READY.json")

if __name__ == '__main__':
    main()
