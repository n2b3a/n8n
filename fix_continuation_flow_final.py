#!/usr/bin/env python3
"""
FIX CRÍTICO: El flujo de continuación revisa awaiting_continuation ANTES de cargar la sesión

PROBLEMA:
  Buscar Usuario (restaurant_people)
    ↓
  ¿Es Continuación? (revisa $json.awaiting_continuation)  ← ❌ Este dato NO existe aún!
    ↓
  Buscar Sesión Activa (line_sessions con awaiting_continuation)

SOLUCIÓN:
  Buscar Usuario (restaurant_people)
    ↓
  Buscar Sesión Activa (line_sessions con awaiting_continuation)  ← Mover ANTES
    ↓
  ¿Es Continuación? (revisa $json.awaiting_continuation)  ← Ahora SÍ tiene el dato
"""

import json
import sys

def fix_continuation_flow_order(workflow):
    """Reorganizar flujo para que Buscar Sesión Activa venga ANTES de ¿Es Continuación?"""
    print("\n" + "="*80)
    print("FIX CRÍTICO: ORDEN DEL FLUJO DE CONTINUACIÓN")
    print("="*80)

    connections = workflow['connections']

    print("\nProblema identificado:")
    print("  ❌ ¿Es Continuación? revisa awaiting_continuation ANTES de cargar sesión")
    print("\nSolución:")
    print("  ✅ Mover Buscar Sesión Activa ANTES de ¿Es Continuación?")

    # Nuevo flujo:
    # Buscar Usuario → Buscar Sesión Activa → ¿Es Continuación?

    # 1. Buscar Usuario → Buscar Sesión Activa
    if 'Buscar Usuario' in connections:
        connections['Buscar Usuario']['main'] = [[{
            'node': 'Buscar Sesión Activa',
            'type': 'main',
            'index': 0
        }]]
        print("\n✅ Buscar Usuario → Buscar Sesión Activa")

    # 2. Buscar Sesión Activa → ¿Es Continuación?
    if 'Buscar Sesión Activa' in connections:
        # Guardar la conexión actual de Buscar Sesión Activa
        original_target = connections['Buscar Sesión Activa']['main'][0] if connections['Buscar Sesión Activa']['main'] else None

        # Nueva conexión: Buscar Sesión Activa → ¿Es Continuación?
        connections['Buscar Sesión Activa']['main'] = [[{
            'node': '¿Es Continuación?',
            'type': 'main',
            'index': 0
        }]]
        print("✅ Buscar Sesión Activa → ¿Es Continuación?")

    # 3. ¿Es Continuación? outputs:
    #    Output 0 (true) → Detectar Opção Continuação
    #    Output 1 (false) → ¿Existe Sesión Onboarding? (flujo normal)

    if '¿Es Continuación?' in connections:
        connections['¿Es Continuación?']['main'] = [
            # Output 0 (true) - Es continuación
            [{
                'node': 'Detectar Opção Continuação',
                'type': 'main',
                'index': 0
            }],
            # Output 1 (false) - No es continuación, continuar flujo normal
            [{
                'node': '¿Existe Sesión Onboarding?',
                'type': 'main',
                'index': 0
            }]
        ]
        print("✅ ¿Es Continuación? [0] → Detectar Opção Continuação")
        print("✅ ¿Es Continuación? [1] → ¿Existe Sesión Onboarding?")

    print("\n✅ Flujo corregido:")
    print("   Buscar Usuario")
    print("     ↓")
    print("   Buscar Sesión Activa (carga awaiting_continuation)")
    print("     ↓")
    print("   ¿Es Continuación? (ahora SÍ tiene el dato)")
    print("     ↓ [0=true]")
    print("   Detectar Opção Continuação")

    return True

def verify_buscar_sesion_returns_field(workflow):
    """Verificar que Buscar Sesión Activa retorna awaiting_continuation"""
    print("\n" + "="*80)
    print("VERIFICAR: BUSCAR SESIÓN ACTIVA")
    print("="*80)

    nodes = workflow['nodes']
    buscar_sesion = next((n for n in nodes if n['name'] == 'Buscar Sesión Activa'), None)

    if not buscar_sesion:
        print("❌ Nodo no encontrado")
        return False

    params = buscar_sesion['parameters']
    print(f"\nNodo: Buscar Sesión Activa")
    print(f"  Tipo: {buscar_sesion['type']}")
    print(f"  Tabla: {params.get('tableId')}")
    print(f"  Operation: {params.get('operation')}")
    print(f"  ReturnAll: {params.get('returnAll')}")

    # Si returnAll es true, retorna TODOS los campos incluido awaiting_continuation
    if params.get('returnAll'):
        print("\n✅ returnAll=true → Retorna TODOS los campos (incluido awaiting_continuation)")
        print("\n⚠️  IMPORTANTE: La tabla line_sessions DEBE tener la columna awaiting_continuation")
        print("   Ejecutar en Supabase:")
        print("   ALTER TABLE line_sessions ADD COLUMN IF NOT EXISTS awaiting_continuation BOOLEAN DEFAULT FALSE;")
    else:
        print("\n⚠️  returnAll=false → Puede que no retorne awaiting_continuation")
        print("   Se recomienda configurar returnAll=true o especificar campos")

    return True

def main():
    print("="*80)
    print("FIX FINAL: FLUJO DE CONTINUACIÓN")
    print("="*80)

    # Cargar workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-PRODUCTION-READY.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"\n✅ Workflow cargado: {len(workflow['nodes'])} nodos")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

    # Aplicar fix
    fix_continuation_flow_order(workflow)
    verify_buscar_sesion_returns_field(workflow)

    # Guardar
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-PRODUCTION-READY.json', 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)

        print("\n" + "="*80)
        print("✅ WORKFLOW CORREGIDO")
        print("="*80)
        print("\n📄 Archivo: workflow-frepi-mvp1-PRODUCTION-READY.json")
        print("\n📋 CAMBIOS:")
        print("   ✅ Flujo reorganizado: Buscar Usuario → Buscar Sesión Activa → ¿Es Continuación?")
        print("   ✅ Ahora awaiting_continuation está disponible cuando se revisa")

        print("\n🎯 PRÓXIMO PASO CRÍTICO:")
        print("\n   Ejecutar en Supabase SQL Editor:")
        print("\n   ALTER TABLE line_sessions")
        print("   ADD COLUMN IF NOT EXISTS awaiting_continuation BOOLEAN DEFAULT FALSE;")

        print("\n   Sin esta columna, el workflow NO funcionará correctamente.")

    except Exception as e:
        print(f"\n❌ Error guardando: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
