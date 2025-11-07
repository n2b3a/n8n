#!/usr/bin/env python3
"""
FASE 1: Desbloquear Menú
- Modificar "Verificar Setup Completo" para siempre retornar true
- Actualizar "GENERATE_MAIN_MENU" con advertencia de perfil incompleto
"""

import json
import sys

def find_node_by_name(nodes, name):
    """Find a node by its name"""
    for node in nodes:
        if node.get('name') == name:
            return node
    return None

def fase1_desbloquear_menu(workflow):
    """FASE 1: Permitir acceso al menú sin preferencias obligatorias"""
    print("=" * 80)
    print("FASE 1: DESBLOQUEAR MENÚ")
    print("=" * 80)

    # Cambio 1.1: Modificar "Verificar Setup Completo"
    print("\n[1.1] Modificando 'Verificar Setup Completo'...")
    setup_node = find_node_by_name(workflow['nodes'], 'Verificar Setup Completo')

    if setup_node:
        # Nuevo código que siempre permite acceso al menú
        nuevo_codigo = '''const usuario = $input.first().json;

// CAMBIO: Siempre permitir acceso al menú
// Solo calculamos el % de completitud para mostrar
const tienePreferencias = usuario.category_preferences &&
                          Object.keys(usuario.category_preferences).length > 0;

console.log(`✅ [Setup Check] Usuario: ${usuario.nome || 'Sin nombre'}`);
console.log(`   Tiene preferencias: ${tienePreferencias}`);
console.log(`   % Completitud: ${usuario.preferencias_porcentaje || 0}%`);

return [{
  json: {
    ...usuario,
    setup_completo: true,  // ✅ SIEMPRE true - menú siempre accesible
    tiene_preferencias: tienePreferencias,  // Flag informativo
    preferencias_porcentaje: usuario.preferencias_porcentaje || 0
  }
}];'''

        setup_node['parameters']['jsCode'] = nuevo_codigo
        print("  ✅ Código actualizado - Menú ahora siempre accesible")
    else:
        print("  ❌ Nodo 'Verificar Setup Completo' no encontrado")
        return False

    # Cambio 1.2: Actualizar "Generar Menú Principal"
    print("\n[1.2] Modificando 'Generar Menú Principal'...")
    menu_node = find_node_by_name(workflow['nodes'], 'Generar Menú Principal')

    if menu_node:
        # Buscar el nodo usando también el ID alternativo
        if not menu_node:
            menu_node = find_node_by_name(workflow['nodes'], 'GENERATE_MAIN_MENU')

        if menu_node:
            nuevo_codigo = '''const usuario = $input.first().json;
const porcentaje = usuario.preferencias_porcentaje || 0;
const phoneNumber = usuario.phone_number || $input.first().json.phone_number;

console.log(`📋 [Generar Menú] Usuario: ${usuario.nome || 'Sin nombre'}`);
console.log(`   Preferencias: ${porcentaje}%`);

// Construir advertencia si perfil incompleto
let advertencia = '';
if (porcentaje < 100) {
  advertencia = `⚠️ *Perfil incompleto (${porcentaje}%)*
→ Configure preferências para melhores recomendações!

`;
}

const menuText = `🍽️ *Bem-vindo ao Frepi!*

${advertencia}Escolha uma opção:

1️⃣ Fazer uma compra
2️⃣ Atualizar preços de fornecedor
3️⃣ Registrar/Atualizar fornecedor
4️⃣ Configurar preferências (${porcentaje}%)${porcentaje < 100 ? ' ⬅️ *Recomendado!*' : ' ✅'}

💬 Você pode digitar o número ou descrever o que precisa.
Exemplo: "quero fazer uma compra" ou "1"`;

return [{
  json: {
    output: menuText,
    phone_number: phoneNumber,
    user_data: usuario,
    is_menu: true
  }
}];'''

            menu_node['parameters']['jsCode'] = nuevo_codigo
            print("  ✅ Menú actualizado con advertencia de perfil incompleto")
        else:
            print("  ❌ Nodo de menú no encontrado")
            return False

    print("\n✅ FASE 1 COMPLETADA")
    return True

def main():
    print("🚀 Iniciando implementación - FASE 1\n")

    # Cargar workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow cargado: {len(workflow['nodes'])} nodos\n")
    except Exception as e:
        print(f"❌ Error cargando workflow: {e}")
        sys.exit(1)

    # Ejecutar Fase 1
    if not fase1_desbloquear_menu(workflow):
        print("\n❌ Error en Fase 1")
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
    print("FASE 1 COMPLETADA CON ÉXITO")
    print("=" * 80)
    print("\nCambios realizados:")
    print("  ✅ Menú accesible sin preferencias obligatorias")
    print("  ✅ Advertencia visual de perfil incompleto")
    print("  ✅ Indicador '⬅️ Recomendado!' en opción de preferencias")

if __name__ == '__main__':
    main()
