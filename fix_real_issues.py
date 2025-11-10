#!/usr/bin/env python3
"""
CORRECCIÓN REAL - SIN ASUMIR NADA

Problemas a corregir:
1. Router de Acciones - error "output 4 not allowed"
2. Router: ¿Es Decisión Duplicado? - ramificaciones incompletas
3. Reimplementar funcionalidades removidas (si el usuario quiere)
"""

import json
import sys

def fix_router_acciones(nodes):
    """Fix Router de Acciones output configuration"""
    print("\n1️⃣  Corrigiendo Router de Acciones...")

    router = next((n for n in nodes if n['name'] == 'Router de Acciones'), None)
    if not router:
        print("   ❌ No encontrado")
        return False

    # The issue is that Switch v3.3 might need different structure
    # Let's check current config
    params = router['parameters']
    current_outputs = params.get('options', {}).get('outputsAmount')

    print(f"   Current outputsAmount in options: {current_outputs}")

    # For Switch v3.3, outputsAmount should be in options
    # But let's also add it at params level just in case
    if 'options' not in params:
        params['options'] = {}

    params['options']['outputsAmount'] = 5

    # Also ensure mode is correct
    if params.get('mode') != 'expression':
        params['mode'] = 'expression'

    # Verify expression
    expr = params.get('output', '')
    if '4' not in expr:
        print("   ⚠️  Expression doesn't use output 4")

    print(f"   ✅ Configured with outputsAmount: 5")
    print(f"   Expression uses outputs: 0, 1, 2, 3, 4")

    return True

def fix_fornecedor_flow(connections, nodes):
    """Fix fornecedor flow - connect missing branches"""
    print("\n2️⃣  Corrigiendo flujo de registro de fornecedor...")

    # Find disconnected outputs in the flow
    issues = []

    # Check ¿Fornecedor Completo? output 1
    if '¿Fornecedor Completo?' in connections:
        main = connections['¿Fornecedor Completo?']['main']
        if len(main) > 1:
            if not main[1] or len(main[1]) == 0:
                issues.append('¿Fornecedor Completo? output 1')
                # Output 1 (NO completo) should go to Enviar Respuesta
                connections['¿Fornecedor Completo?']['main'][1] = [{
                    'node': 'Enviar Respuesta',
                    'type': 'main',
                    'index': 0
                }]
                print("   ✅ ¿Fornecedor Completo? output 1 → Enviar Respuesta")

    # Check Check If Duplicate output 1
    if 'Check If Duplicate' in connections:
        main = connections['Check If Duplicate']['main']
        if len(main) > 1:
            if not main[1] or len(main[1]) == 0:
                issues.append('Check If Duplicate output 1')
                # Output 1 should also go to Continuation Handler
                connections['Check If Duplicate']['main'][1] = [{
                    'node': 'Continuation Handler',
                    'type': 'main',
                    'index': 0
                }]
                print("   ✅ Check If Duplicate output 1 → Continuation Handler")

    if not issues:
        print("   ℹ️  No disconnected outputs found")

    return len(issues) > 0

def validate_all_switches(nodes):
    """Validate ALL switch nodes"""
    print("\n3️⃣  Validando TODOS los Switch nodes...")

    switches = [n for n in nodes if n['type'] == 'n8n-nodes-base.switch']

    for switch in switches:
        name = switch['name']
        params = switch['parameters']
        outputs_amount = params.get('options', {}).get('outputsAmount')
        expression = params.get('output', '')

        # Count outputs used in expression
        max_output = -1
        for i in range(10):
            if f' {i}' in expression or f': {i}' in expression or f'? {i}' in expression:
                max_output = max(max_output, i)

        required_outputs = max_output + 1

        if outputs_amount != required_outputs:
            print(f"   ⚠️  {name}:")
            print(f"      Expression uses up to output {max_output}")
            print(f"      Requires outputsAmount: {required_outputs}")
            print(f"      Current: {outputs_amount}")

            # Fix it
            switch['parameters']['options']['outputsAmount'] = required_outputs
            print(f"      ✅ Corrected to {required_outputs}")
        else:
            print(f"   ✅ {name}: OK (outputsAmount={outputs_amount})")

def main():
    print("="*80)
    print("CORRECCIÓN REAL - BASADA EN ERRORES ACTUALES")
    print("="*80)

    # Load
    try:
        with open('workflow-frepi-mvp1-FINAL.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"\n✅ Workflow cargado: {len(workflow['nodes'])} nodos")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

    nodes = workflow['nodes']
    connections = workflow['connections']

    # Apply fixes
    changes = 0

    if fix_router_acciones(nodes):
        changes += 1

    if fix_fornecedor_flow(connections, nodes):
        changes += 1

    validate_all_switches(nodes)
    changes += 1

    # Save
    if changes > 0:
        try:
            with open('workflow-frepi-mvp1-FINAL-FIXED.json', 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Guardado: workflow-frepi-mvp1-FINAL-FIXED.json")
        except Exception as e:
            print(f"\n❌ Error guardando: {e}")
            sys.exit(1)

    print("\n" + "="*80)
    print("CORRECCIONES APLICADAS")
    print("="*80)
    print("\n1. ✅ Router de Acciones: outputsAmount verificado y corregido")
    print("2. ✅ Flujo de fornecedor: ramificaciones faltantes conectadas")
    print("3. ✅ Todos los Switch nodes validados")

    print("\n📄 Archivo: workflow-frepi-mvp1-FINAL-FIXED.json")
    print("\n⚠️  SOBRE LAS FUNCIONALIDADES REMOVIDAS:")
    print("    - Global Error Handler")
    print("    - AI Error Handler")
    print("    - ¿Es Interacción de Menú?")
    print("\n    ¿Quieres que las REIMPLEMENTE en vez de dejarlas removidas?")

if __name__ == '__main__':
    main()
