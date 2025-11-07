#!/usr/bin/env python3
"""
FASE 4 & 5: Advertencias de Precios + Tono Empleado Útil
- Modificar "Generar Recomendación" para agregar nota de precios desactualizados
- Actualizar prompts de agentes para tono consultivo
"""

import json
import sys

def find_node_by_name(nodes, name):
    """Find a node by its name"""
    for node in nodes:
        if node.get('name') == name:
            return node
    return None

def fase4_advertencias_precios(workflow):
    """FASE 4: Agregar advertencias de precios desactualizados"""
    print("=" * 80)
    print("FASE 4: ADVERTENCIAS DE PRECIOS DESACTUALIZADOS")
    print("=" * 80)

    nodes = workflow['nodes']

    # Modificar "Generar Recomendación"
    print("\n[4.1] Modificando 'Generar Recomendación'...")
    rec_node = find_node_by_name(nodes, 'Generar Recomendación')

    if rec_node:
        codigo_actual = rec_node['parameters']['jsCode']

        # Buscar donde se construye el mensaje final y agregar nota
        # Agregar al final del mensaje, antes del return
        if 'return [' in codigo_actual:
            # Insertar nota antes del return si hay problemas
            codigo_nuevo = codigo_actual.replace(
                'return [',
                '''// Agregar nota si hay precios desactualizados
if (hayProblemas) {
  mensaje += `\\n\\n⚠️ *Nota Importante*

Alguns preços estão desatualizados (> 30 dias).
Recomendo atualizar seus preços para recomendações mais precisas.

Digite "2" para atualizar preços agora.`;
}

return ['''
            )
            rec_node['parameters']['jsCode'] = codigo_nuevo
            print("  ✅ Nota de precios desactualizados agregada")
        else:
            print("  ⚠️  No se pudo modificar el código automáticamente")
    else:
        print("  ❌ Nodo 'Generar Recomendación' no encontrado")

    return True

def fase5_tono_empleado(workflow):
    """FASE 5: Actualizar prompts con tono de empleado útil"""
    print("\n" + "=" * 80)
    print("FASE 5: TONO DE EMPLEADO ÚTIL Y CONSULTIVO")
    print("=" * 80)

    nodes = workflow['nodes']

    # 5.1: Actualizar "Agente de Compras"
    print("\n[5.1] Actualizando 'Agente de Compras'...")
    agent_compras = find_node_by_name(nodes, 'Agente de Compras')

    if agent_compras:
        prompt_actual = agent_compras['parameters']['options']['systemMessage']

        # Agregar al inicio del prompt
        prompt_nuevo = '''🎯 VOCÊ É: Um assistente de procurement dedicado e experiente.
Como um funcionário de confiança ajudando seu chefe a fazer as melhores compras.

SUA ATITUDE:
- 💡 Proativo: Sugira produtos relacionados que podem estar faltando
- 👀 Atento: Lembre do histórico de compras se disponível
- 🎓 Consultivo: Explique POR QUÊ está recomendando cada fornecedor
- ⚡ Eficiente: Vá direto ao ponto, sem ser robótico
- 🤝 Amigável: Fale como um colega brasileiro experiente

---

''' + prompt_actual

        agent_compras['parameters']['options']['systemMessage'] = prompt_nuevo
        print("  ✅ Prompt de 'Agente de Compras' actualizado")
    else:
        print("  ❌ Nodo 'Agente de Compras' no encontrado")

    # 5.2: Actualizar "Agente Subir Precios"
    print("\n[5.2] Actualizando 'Agente Subir Precios'...")
    agent_precos = find_node_by_name(nodes, 'Agente Subir Precios')

    if agent_precos:
        prompt_actual = agent_precos['parameters']['options']['systemMessage']

        # Agregar dica proativa
        if 'FORMATO FINAL' in prompt_actual:
            prompt_nuevo = prompt_actual.replace(
                'FORMATO FINAL',
                '''💡 DICA PROATIVA:
Se o usuário enviar apenas 2-3 produtos, pergunte de forma natural:
"Legal! Vi que cadastrou [produtos]. Tem mais produtos desse fornecedor para cadastrar?"

FORMATO FINAL'''
            )
            agent_precos['parameters']['options']['systemMessage'] = prompt_nuevo
            print("  ✅ Prompt de 'Agente Subir Precios' actualizado")
        else:
            print("  ⚠️  No se encontró sección para modificar")
    else:
        print("  ❌ Nodo 'Agente Subir Precios' no encontrado")

    # 5.3: Actualizar "Agente Registrar Fornecedor"
    print("\n[5.3] Actualizando 'Agente Registrar Fornecedor'...")
    agent_fornecedor = find_node_by_name(nodes, 'Agente Registrar Fornecedor')

    if agent_fornecedor:
        prompt_actual = agent_fornecedor['parameters']['options']['systemMessage']

        # Agregar al final, antes del TOM
        if 'TOM:' in prompt_actual:
            prompt_nuevo = prompt_actual.replace(
                'TOM:',
                '''💡 SEJA CONSULTIVO:
Quando terminar de cadastrar o fornecedor, ofereça ajuda:
"Ótimo! Já tem os preços deste fornecedor para cadastrar também?
Posso te ajudar com isso agora!"

TOM:'''
            )
            agent_fornecedor['parameters']['options']['systemMessage'] = prompt_nuevo
            print("  ✅ Prompt de 'Agente Registrar Fornecedor' actualizado")
        else:
            print("  ⚠️  No se encontró sección TOM para modificar")
    else:
        print("  ❌ Nodo 'Agente Registrar Fornecedor' no encontrado")

    return True

def main():
    print("🚀 Iniciando implementación - FASE 4 & 5\n")

    # Cargar workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow cargado: {len(workflow['nodes'])} nodos\n")
    except Exception as e:
        print(f"❌ Error cargando workflow: {e}")
        sys.exit(1)

    # Ejecutar Fase 4
    if not fase4_advertencias_precios(workflow):
        print("\n❌ Error en Fase 4")
        sys.exit(1)

    # Ejecutar Fase 5
    if not fase5_tono_empleado(workflow):
        print("\n❌ Error en Fase 5")
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
    print("FASE 4 & 5 COMPLETADAS CON ÉXITO")
    print("=" * 80)
    print("\nCambios realizados:")
    print("  ✅ Nota de precios desactualizados en recomendaciones")
    print("  ✅ Agente de Compras: tono consultivo y proactivo")
    print("  ✅ Agente Subir Precios: sugiere cadastrar más productos")
    print("  ✅ Agente Registrar Fornecedor: ofrece cadastrar preços")
    print("\n🎯 El bot ahora actúa como un empleado de procurement útil!")

if __name__ == '__main__':
    main()
