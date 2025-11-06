#!/usr/bin/env python3
"""
Script to implement 3 critical improvements to the Frepi MVP workflow:
1. Natural language menu detection
2. Duplicate supplier verification
3. Clarify recommendation scope
"""

import json
import sys

def find_node_by_name(nodes, name):
    """Find a node by its name"""
    for node in nodes:
        if node.get('name') == name:
            return node
    return None

def find_node_by_id(nodes, node_id):
    """Find a node by its ID"""
    for node in nodes:
        if node.get('id') == node_id:
            return node
    return None

def improve_natural_language_detection(workflow):
    """Improve menu detection to accept natural language input"""
    print("🔧 Improving natural language menu detection...")

    # 1. Update "Detectar Opción del Menú" node
    menu_detector = find_node_by_name(workflow['nodes'], 'Detectar Opción del Menú')
    if menu_detector:
        menu_detector['parameters']['jsCode'] = '''const mensaje = $input.first().json.message.toLowerCase();
const usuario = $input.first().json;

console.log(`🔍 [Detectar Opción] Mensaje recibido: "${mensaje}"`);

// Detectar "Hacer una compra" (Opción 1)
if (mensaje.includes('1') ||
    mensaje.includes('compra') ||
    mensaje.includes('pedido') ||
    mensaje.includes('fazer uma compra') ||
    mensaje.includes('fazer compra') ||
    mensaje.includes('quero comprar') ||
    mensaje.includes('preciso comprar')) {
  console.log('✅ [Detectar Opción] Detectado: HACER_COMPRA');
  return [{
    json: {
      ...usuario,
      accion_detectada: 'HACER_COMPRA',
      output_route: 0
    }
  }];
}

// Detectar "Atualizar preços" (Opción 2)
if (mensaje.includes('2') ||
    mensaje.includes('precio') ||
    mensaje.includes('preço') ||
    mensaje.includes('atualizar preço') ||
    mensaje.includes('cadastrar preço') ||
    mensaje.includes('enviar preço') ||
    mensaje.includes('registrar preço')) {
  console.log('✅ [Detectar Opción] Detectado: ACTUALIZAR_PRECIOS');
  return [{
    json: {
      ...usuario,
      accion_detectada: 'ACTUALIZAR_PRECIOS',
      output_route: 1
    }
  }];
}

// Detectar "Registrar fornecedor" (Opción 3)
if (mensaje.includes('3') ||
    mensaje.includes('fornecedor') ||
    mensaje.includes('registrar fornecedor') ||
    mensaje.includes('cadastrar fornecedor') ||
    mensaje.includes('adicionar fornecedor') ||
    mensaje.includes('novo fornecedor')) {
  console.log('✅ [Detectar Opción] Detectado: REGISTRAR_FORNECEDOR');
  return [{
    json: {
      ...usuario,
      accion_detectada: 'REGISTRAR_FORNECEDOR',
      output_route: 2
    }
  }];
}

// Detectar "Configurar preferências" (Opción 4)
if (mensaje.includes('4') ||
    mensaje.includes('preferencia') ||
    mensaje.includes('preferência') ||
    mensaje.includes('configurar') ||
    mensaje.includes('configuração') ||
    mensaje.includes('config')) {
  console.log('✅ [Detectar Opción] Detectado: CONFIGURAR_PREFERENCIAS');
  return [{
    json: {
      ...usuario,
      accion_detectada: 'CONFIGURAR_PREFERENCIAS',
      output_route: 3
    }
  }];
}

// Si no se detecta ninguna opción válida
console.log('❌ [Detectar Opción] No se detectó ninguna opción válida');
return [{
  json: {
    ...usuario,
    accion_detectada: 'DESCONOCIDA',
    output_route: 4,
    output: `❓ Desculpe, não entendi.

Por favor, escolha uma das opções:

1️⃣ Fazer uma compra
2️⃣ Atualizar preços de fornecedor
3️⃣ Registrar/Atualizar fornecedor
4️⃣ Configurar preferências

Você pode digitar o número ou descrever o que precisa.`
  }
}];'''
        print(f"  ✅ Updated 'Detectar Opción del Menú' node")

    # 2. Update "GENERATE_MAIN_MENU" node
    menu_gen = find_node_by_name(workflow['nodes'], 'GENERATE_MAIN_MENU')
    if menu_gen:
        menu_gen['parameters']['jsCode'] = '''const usuario = $input.first().json;
const porcentaje = usuario.preferencias_porcentaje || 0;
const phoneNumber = usuario.phone_number || $input.first().json.phone_number;

console.log(`📋 [Generar Menú] Usuario: ${usuario.nome || 'Sin nombre'}, Preferencias: ${porcentaje}%`);

const menuText = `🍽️ *Bem-vindo ao Frepi!*

Escolha uma opção:

1️⃣ Fazer uma compra
2️⃣ Atualizar preços de fornecedor
3️⃣ Registrar/Atualizar fornecedor
4️⃣ Configurar preferências (${porcentaje}%)

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
        print(f"  ✅ Updated 'GENERATE_MAIN_MENU' node")

    # 3. Update "DETECT_PREFERENCE_OPTION" node
    pref_detector = find_node_by_name(workflow['nodes'], 'DETECT_PREFERENCE_OPTION')
    if pref_detector:
        pref_detector['parameters']['jsCode'] = '''const mensaje = $input.first().json.message.toLowerCase();
const usuario = $input.first().json;

console.log(`🔍 [Detectar Preferencia] Mensaje: "${mensaje}"`);

// Opción 1: Produtos frequentes
if (mensaje.includes('1') ||
    mensaje.includes('produto') ||
    mensaje.includes('frequente') ||
    mensaje.includes('categoria')) {
  return [{ json: { ...usuario, preference_option: 'produtos', output_route: 0 } }];
}

// Opción 2: Fornecedores preferidos
if (mensaje.includes('2') ||
    mensaje.includes('fornecedor') ||
    mensaje.includes('preferido')) {
  return [{ json: { ...usuario, preference_option: 'fornecedores', output_route: 1 } }];
}

// Opción 3: Frequência de compras
if (mensaje.includes('3') ||
    mensaje.includes('frequência') ||
    mensaje.includes('frequencia') ||
    mensaje.includes('compra')) {
  return [{ json: { ...usuario, preference_option: 'frequencia', output_route: 2 } }];
}

// Opción 4: Orçamento mensal
if (mensaje.includes('4') ||
    mensaje.includes('orçamento') ||
    mensaje.includes('orcamento') ||
    mensaje.includes('gasto') ||
    mensaje.includes('budget')) {
  return [{ json: { ...usuario, preference_option: 'orcamento', output_route: 3 } }];
}

// Opción 5: Condições de pagamento
if (mensaje.includes('5') ||
    mensaje.includes('pagamento') ||
    mensaje.includes('condição') ||
    mensaje.includes('condicao')) {
  return [{ json: { ...usuario, preference_option: 'pagamento', output_route: 4 } }];
}

// Opción 6: Voltar ao menu principal
if (mensaje.includes('6') ||
    mensaje.includes('voltar') ||
    mensaje.includes('menu') ||
    mensaje.includes('sair')) {
  return [{ json: { ...usuario, preference_option: 'voltar', output_route: 5 } }];
}

// No se detectó opción válida
return [{
  json: {
    ...usuario,
    preference_option: 'desconocida',
    output_route: 6,
    output: `❓ Desculpe, não entendi. Por favor escolha uma opção de 1 a 6.`
  }
}];'''
        print(f"  ✅ Updated 'DETECT_PREFERENCE_OPTION' node")

    # 4. Update "GENERATE_PREFERENCES_SUBMENU" node
    submenu_gen = find_node_by_name(workflow['nodes'], 'GENERATE_PREFERENCES_SUBMENU')
    if submenu_gen:
        submenu_gen['parameters']['jsCode'] = '''const usuario = $input.first().json;
const porcentaje = usuario.preferencias_porcentaje || 0;
const phoneNumber = usuario.phone_number;

const submenu = `⚙️ *PREFERÊNCIAS* (${porcentaje}% completo)

Escolha o que deseja configurar:

1️⃣ Produtos frequentes
2️⃣ Fornecedores preferidos
3️⃣ Frequência de compras
4️⃣ Orçamento mensal
5️⃣ Condições de pagamento
6️⃣ Voltar ao menu principal

💬 Digite o número ou descreva o que precisa.`;

return [{
  json: {
    output: submenu,
    phone_number: phoneNumber,
    user_data: usuario,
    is_submenu: true
  }
}];'''
        print(f"  ✅ Updated 'GENERATE_PREFERENCES_SUBMENU' node")

def add_duplicate_supplier_check(workflow):
    """Add duplicate supplier verification with user choice"""
    print("🔧 Adding duplicate supplier verification...")

    # Update "SAVE_FORNECEDOR_DB" node
    save_node = find_node_by_name(workflow['nodes'], 'SAVE_FORNECEDOR_DB')
    if save_node:
        save_node['parameters']['jsCode'] = '''const fornecedorData = $input.first().json;
const phoneNumber = fornecedorData.phone_number;
const restaurantId = fornecedorData.restaurant_id;

// Parse datos del fornecedor
const texto = fornecedorData.output;
const lineas = texto.split('\\n');

const datos = {};
for (const linea of lineas) {
  if (linea.startsWith('Nome:')) {
    datos.nome = linea.replace('Nome:', '').trim();
  } else if (linea.startsWith('Telefone:')) {
    datos.telefone = linea.replace('Telefone:', '').trim();
  } else if (linea.startsWith('Dias:')) {
    datos.dias = linea.replace('Dias:', '').trim();
  } else if (linea.startsWith('Produtos:')) {
    const produtosStr = linea.replace('Produtos:', '').trim();
    datos.produtos = produtosStr.split(',').map(p => p.trim());
  }
}

console.log('📦 [Salvar Fornecedor] Dados extraídos:', dados);

// ⚠️ CHECK FOR DUPLICATES
const { data: existingSuppliers, error: searchError } = await $supabase
  .from('suppliers')
  .select('id, company_name, whatsapp_number')
  .ilike('company_name', `%${datos.nome}%`)
  .limit(5);

if (searchError) {
  console.error('❌ [Salvar Fornecedor] Erro ao buscar duplicados:', searchError);
}

// If similar supplier found, ask user
if (existingSuppliers && existingSuppliers.length > 0) {
  console.log(`⚠️ [Salvar Fornecedor] ${existingSuppliers.length} fornecedor(es) similar(es) encontrado(s)`);

  let duplicatesText = existingSuppliers.map((s, idx) =>
    `   ${idx + 1}. *${s.company_name}* (${s.whatsapp_number || 'sem telefone'})`
  ).join('\\n');

  const warningMessage = `⚠️ *Fornecedor já existe!*

Encontrei fornecedor(es) com nome similar:

${duplicatesText}

O que deseja fazer?

1️⃣ Criar novo fornecedor mesmo assim
2️⃣ Atualizar dados do primeiro da lista
3️⃣ Cancelar

💬 Digite o número da opção.`;

  return [{
    json: {
      duplicate_found: true,
      existing_suppliers: existingSuppliers,
      new_supplier_data: datos,
      phone_number: phoneNumber,
      restaurant_id: restaurantId,
      output: warningMessage,
      needs_user_decision: true
    }
  }];
}

// No duplicate found - proceed with creation
console.log('✅ [Salvar Fornecedor] No se encontraron duplicados, creando nuevo...');

const { data: newSupplier, error: insertError } = await $supabase
  .from('suppliers')
  .insert({
    company_name: datos.nome,
    whatsapp_number: datos.telefone,
    delivery_days: { dias: datos.dias },
    is_active: true,
    created_at: new Date().toISOString()
  })
  .select('id')
  .single();

if (insertError) {
  console.error('❌ [Salvar Fornecedor] Erro ao insertar:', insertError);
  return [{
    json: {
      success: false,
      error: insertError.message,
      output: `❌ Erro ao cadastrar fornecedor: ${insertError.message}`,
      phone_number: phoneNumber
    }
  }];
}

const supplierId = newSupplier.id;
console.log(`✅ [Salvar Fornecedor] Fornecedor criado com ID: ${supplierId}`);

// Link products
if (datos.produtos && datos.produtos.length > 0) {
  for (const produto of datos.produtos) {
    await $supabase
      .from('supplier_mapped_products')
      .insert({
        supplier_id: supplierId,
        supplier_product_name: produto,
        current_unit_price: 0,
        is_active: true
      });
  }
  console.log(`✅ [Salvar Fornecedor] ${datos.produtos.length} produto(s) vinculado(s)`);
}

const successMessage = `✅ *Fornecedor cadastrado com sucesso!*

📦 *${datos.nome}*
📞 ${datos.telefone}
📅 Entrega: ${datos.dias}
📦 ${datos.produtos.length} produto(s) vinculado(s)

Digite "menu" para voltar ao menu principal.`;

return [{
  json: {
    success: true,
    supplier_id: supplierId,
    supplier_data: datos,
    output: successMessage,
    phone_number: phoneNumber
  }
}];'''
        print(f"  ✅ Updated 'SAVE_FORNECEDOR_DB' node with duplicate check")

    # Now we need to add a NEW node to handle user's duplicate decision
    # Find the next available position
    max_pos_y = max([node['position'][1] for node in workflow['nodes']])

    duplicate_handler_node = {
        "id": "HANDLE_DUPLICATE_SUPPLIER_DECISION",
        "name": "Handle Duplicate Decision",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1860, max_pos_y + 200],
        "parameters": {
            "language": "javaScript",
            "jsCode": '''const input = $input.first().json;
const mensaje = input.message.toLowerCase();
const existingSuppliers = input.existing_suppliers;
const newSupplierData = input.new_supplier_data;
const phoneNumber = input.phone_number;

console.log(`🔀 [Handle Duplicate] Opción elegida: "${mensaje}"`);

// Opción 1: Crear nuevo de todos modos
if (mensaje.includes('1') || mensaje.includes('criar') || mensaje.includes('novo')) {
  console.log('✅ [Handle Duplicate] Usuario eligió: CREAR NUEVO');

  const { data: newSupplier, error: insertError } = await $supabase
    .from('suppliers')
    .insert({
      company_name: newSupplierData.nome,
      whatsapp_number: newSupplierData.telefone,
      delivery_days: { dias: newSupplierData.dias },
      is_active: true,
      created_at: new Date().toISOString()
    })
    .select('id')
    .single();

  if (insertError) {
    return [{
      json: {
        success: false,
        error: insertError.message,
        output: `❌ Erro ao cadastrar: ${insertError.message}`,
        phone_number: phoneNumber
      }
    }];
  }

  const supplierId = newSupplier.id;

  // Link products
  if (newSupplierData.produtos && newSupplierData.produtos.length > 0) {
    for (const produto of newSupplierData.produtos) {
      await $supabase
        .from('supplier_mapped_products')
        .insert({
          supplier_id: supplierId,
          supplier_product_name: produto,
          current_unit_price: 0,
          is_active: true
        });
    }
  }

  return [{
    json: {
      success: true,
      action: 'created_new',
      supplier_id: supplierId,
      output: `✅ *Novo fornecedor cadastrado!*\\n\\n📦 *${newSupplierData.nome}*\\n\\nDigite "menu" para voltar.`,
      phone_number: phoneNumber
    }
  }];
}

// Opción 2: Atualizar existente
if (mensaje.includes('2') || mensaje.includes('atualizar') || mensaje.includes('sobrescrever')) {
  console.log('✅ [Handle Duplicate] Usuario eligió: ATUALIZAR EXISTENTE');

  const targetSupplier = existingSuppliers[0]; // First one

  const { error: updateError } = await $supabase
    .from('suppliers')
    .update({
      whatsapp_number: newSupplierData.telefone,
      delivery_days: { dias: newSupplierData.dias },
      updated_at: new Date().toISOString()
    })
    .eq('id', targetSupplier.id);

  if (updateError) {
    return [{
      json: {
        success: false,
        error: updateError.message,
        output: `❌ Erro ao atualizar: ${updateError.message}`,
        phone_number: phoneNumber
      }
    }];
  }

  // Add new products
  if (newSupplierData.produtos && newSupplierData.produtos.length > 0) {
    for (const produto of newSupplierData.produtos) {
      await $supabase
        .from('supplier_mapped_products')
        .insert({
          supplier_id: targetSupplier.id,
          supplier_product_name: produto,
          current_unit_price: 0,
          is_active: true
        });
    }
  }

  return [{
    json: {
      success: true,
      action: 'updated_existing',
      supplier_id: targetSupplier.id,
      output: `✅ *Fornecedor atualizado!*\\n\\n📦 *${targetSupplier.company_name}*\\n\\nDigite "menu" para voltar.`,
      phone_number: phoneNumber
    }
  }];
}

// Opción 3: Cancelar
if (mensaje.includes('3') || mensaje.includes('cancelar') || mensaje.includes('não')) {
  console.log('❌ [Handle Duplicate] Usuario eligió: CANCELAR');

  return [{
    json: {
      success: false,
      action: 'cancelled',
      output: `❌ Cadastro cancelado.\\n\\nDigite "menu" para voltar ao menu principal.`,
      phone_number: phoneNumber
    }
  }];
}

// No valid option
return [{
  json: {
    output: `❓ Por favor, escolha uma opção válida (1, 2 ou 3).`,
    phone_number: phoneNumber,
    needs_user_decision: true
  }
}];'''
        }
    }

    workflow['nodes'].append(duplicate_handler_node)
    print(f"  ✅ Added 'Handle Duplicate Decision' node")

    # Add connection from SAVE_FORNECEDOR_DB to new handler when duplicate found
    # We'll need to add a Switch/IF node to route based on duplicate_found flag
    duplicate_router_node = {
        "id": "CHECK_IF_DUPLICATE",
        "name": "Check If Duplicate",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": [1660, max_pos_y + 200],
        "parameters": {
            "conditions": {
                "boolean": [
                    {
                        "value1": "={{ $json.duplicate_found }}",
                        "value2": True
                    }
                ]
            }
        }
    }

    workflow['nodes'].append(duplicate_router_node)
    print(f"  ✅ Added 'Check If Duplicate' router node")

    # Update connections - redirect SAVE_FORNECEDOR_DB through duplicate checker
    if 'SAVE_FORNECEDOR_DB' in workflow['connections']:
        original_target = workflow['connections']['SAVE_FORNECEDOR_DB']['main'][0][0]['node']
        print(f"  📌 Original connection: SAVE_FORNECEDOR_DB -> {original_target}")

        # Redirect to CHECK_IF_DUPLICATE
        workflow['connections']['SAVE_FORNECEDOR_DB'] = {
            "main": [
                [
                    {
                        "node": "CHECK_IF_DUPLICATE",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }

        # Add connections from router
        workflow['connections']['CHECK_IF_DUPLICATE'] = {
            "main": [
                [
                    # True path - has duplicate, send warning and wait for user decision
                    {
                        "node": "Enviar Respuesta",  # Send warning message
                        "type": "main",
                        "index": 0
                    }
                ],
                [
                    # False path - no duplicate, send success message
                    {
                        "node": original_target,  # Original target (Enviar Respuesta)
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }

        # Connect duplicate handler to wait for response
        workflow['connections']['HANDLE_DUPLICATE_SUPPLIER_DECISION'] = {
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

        print(f"  ✅ Connections updated successfully")

    # Note: When duplicate is found, the warning message is sent and user replies normally
    # The HANDLE_DUPLICATE_SUPPLIER_DECISION node will be triggered when the user
    # responds with their choice (1, 2, or 3)
    # We'll need to add routing logic to detect when a message is a duplicate decision

def clarify_recommendation_scope(workflow):
    """Clarify that recommendations are for decision support only, not auto-sending orders"""
    print("🔧 Clarifying recommendation scope...")

    # 1. Update "GENERATE_RECOMMENDATION" node
    rec_gen = find_node_by_name(workflow['nodes'], 'GENERATE_RECOMMENDATION')
    if rec_gen:
        # Find and update the JavaScript code
        current_code = rec_gen['parameters']['jsCode']

        # Replace the final confirmation message
        updated_code = current_code.replace(
            "mensaje += 'Confirma o pedido? 👍';",
            """mensaje += `

━━━━━━━━━━━━━━━━━━━━━━
💡 *IMPORTANTE*

Esta é uma *recomendação* para te ajudar a decidir.
Você precisa fazer o pedido *diretamente com os fornecedores*.

Frepi NÃO envia pedidos automaticamente.

Deseja salvar estas informações para referência? (Sim/Não)`;"""
        )

        rec_gen['parameters']['jsCode'] = updated_code
        print(f"  ✅ Updated 'GENERATE_RECOMMENDATION' node")

    # 2. Update "Agente de Compras" system prompt
    agent_compras = find_node_by_name(workflow['nodes'], 'Agente de Compras')
    if agent_compras and 'options' in agent_compras['parameters']:
        current_prompt = agent_compras['parameters']['options'].get('systemMessage', '')

        # Add clarification if not already present
        if 'NÃO envia pedidos automaticamente' not in current_prompt:
            # Find the mission line and add clarification after it
            updated_prompt = current_prompt.replace(
                '🎯 SUA MISSÃO: Ajudar o restaurante a fazer um pedido de produtos',
                '''🎯 SUA MISSÃO: Ajudar o restaurante a fazer um pedido de produtos

⚠️ *IMPORTANTE*:
Você NÃO envia pedidos automaticamente aos fornecedores.
Você APENAS recomenda as melhores opções baseado nos preços cadastrados.
O restaurante fará o pedido DIRETAMENTE com os fornecedores escolhidos.'''
            )

            agent_compras['parameters']['options']['systemMessage'] = updated_prompt
            print(f"  ✅ Updated 'Agente de Compras' system prompt")
        else:
            print(f"  ℹ️  'Agente de Compras' already has clarification")

    # 3. Update any "Recomendación" related response messages
    # Find nodes that generate shopping list recommendations
    for node in workflow['nodes']:
        if 'jsCode' in node.get('parameters', {}):
            code = node['parameters']['jsCode']
            if 'recomendación' in code.lower() or 'recomendacao' in code.lower():
                if 'Confirma o pedido' in code or 'confirmar pedido' in code.lower():
                    # Update to clarify scope
                    code = code.replace(
                        'Confirma o pedido',
                        'Esta é uma recomendação. Você precisa fazer o pedido diretamente com os fornecedores'
                    )
                    node['parameters']['jsCode'] = code
                    print(f"  ✅ Updated recommendation scope in node '{node['name']}'")

def main():
    print("🚀 Starting workflow improvements...\n")

    # Load workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Loaded workflow with {len(workflow['nodes'])} nodes\n")
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

    # Apply improvements
    try:
        improve_natural_language_detection(workflow)
        print()

        add_duplicate_supplier_check(workflow)
        print()

        clarify_recommendation_scope(workflow)
        print()

    except Exception as e:
        print(f"❌ Error during improvements: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Save updated workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved updated workflow with {len(workflow['nodes'])} nodes")
        print(f"📁 File: /home/user/n8n/workflow-frepi-mvp1-mejorado.json")
    except Exception as e:
        print(f"❌ Error saving workflow: {e}")
        sys.exit(1)

    print("\n✨ All improvements completed successfully!")

if __name__ == '__main__':
    main()
