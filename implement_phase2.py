#!/usr/bin/env python3
"""
FASE 2: Vuelta al Menú - Sistema de Continuación
- Crear nodo "Preguntar Continuação"
- Crear nodo "Detectar Opção Continuação"
- Crear nodo "Router Continuação"
- Conectar todos los flujos a este sistema
"""

import json
import sys

def find_node_by_name(nodes, name):
    """Find a node by its name"""
    for node in nodes:
        if node.get('name') == name:
            return node
    return None

def fase2_vuelta_menu(workflow):
    """FASE 2: Sistema de continuación para volver al menú"""
    print("=" * 80)
    print("FASE 2: VUELTA AL MENÚ - SISTEMA DE CONTINUACIÓN")
    print("=" * 80)

    nodes = workflow['nodes']
    connections = workflow['connections']

    # Encontrar la posición Y más baja para colocar los nuevos nodos
    max_y = max([node['position'][1] for node in nodes])

    # Cambio 2.1: Crear nodo "Preguntar Continuação"
    print("\n[2.1] Creando nodo 'Preguntar Continuação'...")

    preguntar_node = {
        "id": "PREGUNTAR_CONTINUACAO",
        "name": "Preguntar Continuação",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2200, max_y + 200],
        "parameters": {
            "language": "javaScript",
            "jsCode": '''const input = $input.first().json;
const phoneNumber = input.phone_number;
const usuario = input.user_data || input;

console.log(`💬 [Continuação] Preguntando al usuario qué más necesita`);

const mensagemContinuacao = `✅ *Pronto!*

💬 Posso te ajudar com algo mais?

1️⃣ Fazer outra compra
2️⃣ Atualizar preços
3️⃣ Registrar fornecedor
4️⃣ Ver menú principal

Digite o número ou descreva o que precisa.`;

return [{
  json: {
    output: mensagemContinuacao,
    phone_number: phoneNumber,
    user_data: usuario,
    awaiting_continuation: true
  }
}];'''
        }
    }

    nodes.append(preguntar_node)
    print("  ✅ Nodo 'Preguntar Continuação' creado")

    # Cambio 2.2: Crear nodo "Detectar Opção Continuação"
    print("\n[2.2] Creando nodo 'Detectar Opção Continuação'...")

    detectar_node = {
        "id": "DETECTAR_OPCAO_CONTINUACAO",
        "name": "Detectar Opção Continuação",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2200, max_y + 400],
        "parameters": {
            "language": "javaScript",
            "jsCode": '''const mensaje = $input.first().json.message.toLowerCase();
const usuario = $input.first().json;

console.log(`🔍 [Continuação] Mensaje: "${mensaje}"`);

// Opción 1: Fazer outra compra
if (mensaje.includes('1') ||
    mensaje.includes('compra') ||
    mensaje.includes('pedido') ||
    mensaje.includes('fazer compra') ||
    mensaje.includes('outra compra')) {
  console.log('✅ [Continuação] Detectado: FAZER_COMPRA');
  return [{
    json: {
      ...usuario,
      continuation_action: 'FAZER_COMPRA',
      output_route: 0
    }
  }];
}

// Opción 2: Atualizar preços
if (mensaje.includes('2') ||
    mensaje.includes('preço') ||
    mensaje.includes('atualizar') ||
    mensaje.includes('cadastrar preço')) {
  console.log('✅ [Continuação] Detectado: ATUALIZAR_PRECOS');
  return [{
    json: {
      ...usuario,
      continuation_action: 'ATUALIZAR_PRECOS',
      output_route: 1
    }
  }];
}

// Opción 3: Registrar fornecedor
if (mensaje.includes('3') ||
    mensaje.includes('fornecedor') ||
    mensaje.includes('registrar fornecedor')) {
  console.log('✅ [Continuação] Detectado: REGISTRAR_FORNECEDOR');
  return [{
    json: {
      ...usuario,
      continuation_action: 'REGISTRAR_FORNECEDOR',
      output_route: 2
    }
  }];
}

// Opción 4 o por defecto: Ver menú principal
if (mensaje.includes('4') ||
    mensaje.includes('menu') ||
    mensaje.includes('voltar') ||
    mensaje.includes('não') ||
    mensaje.includes('nao')) {
  console.log('✅ [Continuação] Detectado: MOSTRAR_MENU');
  return [{
    json: {
      ...usuario,
      continuation_action: 'MOSTRAR_MENU',
      output_route: 3
    }
  }];
}

// Por defecto, volver al menú
console.log('⚠️ [Continuação] Opción no reconocida, volviendo al menú');
return [{
  json: {
    ...usuario,
    continuation_action: 'MOSTRAR_MENU',
    output_route: 3
  }
}];'''
        }
    }

    nodes.append(detectar_node)
    print("  ✅ Nodo 'Detectar Opção Continuação' creado")

    # Cambio 2.3: Crear nodo "Router Continuação"
    print("\n[2.3] Creando nodo 'Router Continuação'...")

    router_node = {
        "id": "ROUTER_CONTINUACAO",
        "name": "Router Continuação",
        "type": "n8n-nodes-base.switch",
        "typeVersion": 3.3,
        "position": [2200, max_y + 600],
        "parameters": {
            "mode": "expression",
            "output": "=Output (0): {{ $json.continuation_action === 'FAZER_COMPRA' }}\nOutput (1): {{ $json.continuation_action === 'ATUALIZAR_PRECOS' }}\nOutput (2): {{ $json.continuation_action === 'REGISTRAR_FORNECEDOR' }}\nOutput (3): {{ $json.continuation_action === 'MOSTRAR_MENU' }}"
        }
    }

    nodes.append(router_node)
    print("  ✅ Nodo 'Router Continuação' creado")

    # Cambio 2.4: Conectar los nuevos nodos entre sí
    print("\n[2.4] Conectando nuevos nodos...")

    # Preguntar → Enviar Respuesta (para mostrar el mensaje)
    connections['Preguntar Continuação'] = {
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
    print("  ✅ Preguntar Continuação → Enviar Respuesta")

    # Detectar → Router
    connections['Detectar Opção Continuação'] = {
        "main": [
            [
                {
                    "node": "Router Continuação",
                    "type": "main",
                    "index": 0
                }
            ]
        ]
    }
    print("  ✅ Detectar Opção Continuação → Router Continuação")

    # Router → 4 salidas
    connections['Router Continuação'] = {
        "main": [
            [
                {
                    "node": "Crear Sesión de Compra",
                    "type": "main",
                    "index": 0
                }
            ],
            [
                {
                    "node": "Preparar Datos Subir Precios",
                    "type": "main",
                    "index": 0
                }
            ],
            [
                {
                    "node": "Agente Registrar Fornecedor",
                    "type": "main",
                    "index": 0
                }
            ],
            [
                {
                    "node": "Generar Menú Principal",
                    "type": "main",
                    "index": 0
                }
            ]
        ]
    }
    print("  ✅ Router Continuação → 4 acciones")
    print("     Output 0 → Crear Sesión de Compra")
    print("     Output 1 → Preparar Datos Subir Precios")
    print("     Output 2 → Agente Registrar Fornecedor")
    print("     Output 3 → Generar Menú Principal")

    print("\n✅ FASE 2 COMPLETADA")
    print(f"   Nodos totales: {len(nodes)}")
    return True

def main():
    print("🚀 Iniciando implementación - FASE 2\n")

    # Cargar workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow cargado: {len(workflow['nodes'])} nodos\n")
    except Exception as e:
        print(f"❌ Error cargando workflow: {e}")
        sys.exit(1)

    # Ejecutar Fase 2
    if not fase2_vuelta_menu(workflow):
        print("\n❌ Error en Fase 2")
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
    print("FASE 2 COMPLETADA CON ÉXITO")
    print("=" * 80)
    print("\nCambios realizados:")
    print("  ✅ Nodo 'Preguntar Continuação' creado")
    print("  ✅ Nodo 'Detectar Opção Continuação' creado")
    print("  ✅ Nodo 'Router Continuação' creado")
    print("  ✅ Conexiones establecidas entre nuevos nodos")
    print("\nPróximo paso: Conectar flujos existentes a este sistema")

if __name__ == '__main__':
    main()
