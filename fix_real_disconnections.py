#!/usr/bin/env python3
"""
ARREGLAR LOS NODOS QUE REALMENTE ROMPÍ
- ¿Usuario Existe?
- Router: ¿Es Decisión Duplicado?
"""

import json
import sys

def fix_usuario_existe_flow(workflow):
    """Reconectar ¿Usuario Existe? al flujo"""
    print("\n" + "="*80)
    print("ARREGLANDO: ¿USUARIO EXISTE?")
    print("="*80)

    connections = workflow['connections']

    print("\nProblema: Lo desconecté cuando cambié el flujo de continuación")
    print("\nFlujo correcto:")
    print("  Buscar Sesión Activa")
    print("    ↓")
    print("  ¿Es Continuación?")
    print("    ↓ [0=true] → Detectar Opção Continuação")
    print("    ↓ [1=false]")
    print("  ¿Usuario Existe? ← RECONECTAR AQUÍ")
    print("    ↓ [0=true] → Calcular % Preferencias")
    print("    ↓ [1=false]")
    print("  ¿Existe Sesión Onboarding?")

    # Reconectar
    if '¿Es Continuación?' in connections:
        connections['¿Es Continuación?']['main'][1] = [{
            'node': '¿Usuario Existe?',
            'type': 'main',
            'index': 0
        }]
        print("\n✅ Reconectado: ¿Es Continuación? [1] → ¿Usuario Existe?")

    # ¿Usuario Existe? output 1 debe ir a ¿Existe Sesión Onboarding?
    if '¿Usuario Existe?' in connections:
        # Output 0 ya está OK (Calcular % Preferencias)
        # Output 1 debe ir a ¿Existe Sesión Onboarding?
        connections['¿Usuario Existe?']['main'][1] = [{
            'node': '¿Existe Sesión Onboarding?',
            'type': 'main',
            'index': 0
        }]
        print("✅ Conectado: ¿Usuario Existe? [1] → ¿Existe Sesión Onboarding?")

    return True

def fix_router_duplicado_flow(workflow):
    """Conectar Router: ¿Es Decisión Duplicado? al flujo"""
    print("\n" + "="*80)
    print("ARREGLANDO: ROUTER: ¿ES DECISIÓN DUPLICADO?")
    print("="*80)

    connections = workflow['connections']

    print("\nProblema: Check If Duplicate output 1 está desconectado")
    print("\nFlujo correcto:")
    print("  Check If Duplicate")
    print("    ↓ [0] → Continuation Handler (no duplicado)")
    print("    ↓ [1] → Router: ¿Es Decisión Duplicado? (es duplicado) ← CONECTAR AQUÍ")

    # Conectar Check If Duplicate output 1 al Router
    if 'Check If Duplicate' in connections:
        if len(connections['Check If Duplicate']['main']) < 2:
            connections['Check If Duplicate']['main'].append([])

        connections['Check If Duplicate']['main'][1] = [{
            'node': 'Router: ¿Es Decisión Duplicado?',
            'type': 'main',
            'index': 0
        }]
        print("\n✅ Conectado: Check If Duplicate [1] → Router: ¿Es Decisión Duplicado?")

    return True

def verify_fixes(workflow):
    """Verificar que los nodos ya no están huérfanos"""
    print("\n" + "="*80)
    print("VERIFICACIÓN")
    print("="*80)

    connections = workflow['connections']

    # Verificar ¿Usuario Existe?
    incoming = []
    for source, conn_data in connections.items():
        if 'main' in conn_data:
            for i, output_array in enumerate(conn_data['main']):
                if output_array:
                    for target in output_array:
                        if target['node'] == '¿Usuario Existe?':
                            incoming.append(f'{source} [output {i}]')

    print(f"\n¿Usuario Existe?:")
    if incoming:
        print(f"  ✅ Incoming: {incoming[0]}")
    else:
        print(f"  ❌ TODAVÍA HUÉRFANO")

    # Verificar Router: ¿Es Decisión Duplicado?
    incoming = []
    for source, conn_data in connections.items():
        if 'main' in conn_data:
            for i, output_array in enumerate(conn_data['main']):
                if output_array:
                    for target in output_array:
                        if target['node'] == 'Router: ¿Es Decisión Duplicado?':
                            incoming.append(f'{source} [output {i}]')

    print(f"\nRouter: ¿Es Decisión Duplicado?:")
    if incoming:
        print(f"  ✅ Incoming: {incoming[0]}")
    else:
        print(f"  ❌ TODAVÍA HUÉRFANO")

def main():
    print("="*80)
    print("ARREGLAR NODOS QUE ROMPÍ")
    print("="*80)

    # Cargar
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-PRODUCTION-READY.json', 'r') as f:
            workflow = json.load(f)
        print(f"\n✅ Workflow cargado")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

    # Arreglar
    fix_usuario_existe_flow(workflow)
    fix_router_duplicado_flow(workflow)
    verify_fixes(workflow)

    # Guardar
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-PRODUCTION-READY.json', 'w') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        print("\n" + "="*80)
        print("✅ WORKFLOW CORREGIDO")
        print("="*80)
        print("\n📄 Archivo: workflow-frepi-mvp1-PRODUCTION-READY.json")
    except Exception as e:
        print(f"\n❌ Error guardando: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
