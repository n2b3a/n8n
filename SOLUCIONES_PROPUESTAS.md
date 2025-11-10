# ✅ SOLUCIONES PROPUESTAS - Workflow Frepi MVP1

## Resumen
Este documento contiene las soluciones específicas para corregir los problemas identificados en el workflow.

---

## SOLUCIÓN 1: Conectar Flujo de Continuación

### Problema
"Detectar Opção Continuação" está desconectado del flujo principal.

### Solución

#### A. Crear nodo "Verificar Si Es Continuación"

**Tipo:** Code
**Posición:** Después de "Buscar Usuario"
**Código:**

```javascript
// Verificar si es una respuesta a un mensaje de continuación
const usuario = $input.first().json;
const mensaje = $('Extraer Datos WhatsApp').first().json.message;
const phoneNumber = $('Extraer Datos WhatsApp').first().json.phone_number;

// Buscar si hay sesión reciente esperando continuación
const { data: pendingSession } = await $supabase
  .from('line_sessions')
  .select('*')
  .eq('channel_id', phoneNumber)
  .not('session_end', 'is', null)
  .order('session_end', { ascending: false })
  .limit(1)
  .single();

// Verificar si la sesión terminó en los últimos 5 minutos
const isContinuation = pendingSession &&
  (new Date() - new Date(pendingSession.session_end)) < 5 * 60 * 1000 &&
  pendingSession.awaiting_continuation === true;

console.log(`[Verificar Continuación] Es continuación: ${isContinuation}`);

return [{
  json: {
    ...usuario,
    is_continuation: isContinuation,
    previous_session: pendingSession,
    message: mensaje,
    phone_number: phoneNumber
  }
}];
```

#### B. Agregar nodo IF "¿Es Continuación?"

**Condición:** `{{ $json.is_continuation }} === true`

**Salidas:**
- TRUE → "Detectar Opção Continuação"
- FALSE → "Calcular % Preferencias" (flujo normal)

#### C. Modificar "Continuation Handler"

Agregar campo para marcar sesión como esperando continuación:

```javascript
// En el resultado final
return [{
  json: {
    ...data,
    output: continuationMessage,
    phone_number: phoneNumber,
    awaiting_continuation: true,  // ✅ AGREGAR ESTO
    _session_update: {
      ...sessionUpdate,
      awaiting_continuation: true  // ✅ Y ESTO
    }
  }
}];
```

#### D. Actualizar "Update Session DB"

Agregar campo `awaiting_continuation` al update:

```json
{
  "fieldId": "awaiting_continuation",
  "fieldValue": "={{ $json._session_update?.awaiting_continuation || false }}"
}
```

### Diagrama del Flujo Corregido

```
WhatsApp Trigger
    ↓
Config Global
    ↓
Extraer Datos WhatsApp
    ↓
¿Archivo No Soportado? → SI → Enviar Respuesta
    ↓ NO
Buscar Usuario
    ↓
¿Usuario Existe? → NO → Onboarding
    ↓ SI
[NUEVO] Verificar Si Es Continuación
    ↓
[NUEVO] ¿Es Continuación?
    ↓ SI                     ↓ NO
Detectar Opção          Calcular % Preferencias
Continuação                 ↓
    ↓                   (flujo normal)
Router Continuação
```

---

## SOLUCIÓN 2: Conectar Router de Opciones

### Problema
"Router de Opciones" no tiene conexión de entrada y "Detectar Opción del Menú" no se usa correctamente.

### Solución

#### A. Eliminar "Detectar Opción del Menú" y "Router de Opciones"

Estos nodos están duplicados. Ya existe:
- "Detectar Acción del Agente" - que detecta la acción
- "Router de Acciones" - que enruta

**Acción:** ELIMINAR los nodos:
- "Detectar Opción del Menú" (ID: 26039ec0-e676-4a43-9442-1d400acb575b)
- "Router de Opciones" (ID: 40156080-5c02-4d4b-aa6b-f9f4fbeb309f)

#### B. Eliminar "¿Es Interacción de Menú?"

Este nodo también está duplicado. La lógica ya está en el flujo principal.

**Acción:** ELIMINAR nodo (ID: d88ea515-57c8-492a-9a59-8103072a6d0c)

#### C. Simplificar Flujo de Menú

```
Verificar Setup Completo
    ↓
¿Setup Completo? → NO → Crear Sesión de Setup
    ↓ SI                    ↓
Generar Menú Principal  Agente de Setup
    ↓
Enviar Respuesta
```

El usuario responderá con su elección, y en la siguiente interacción:

```
(Nueva interacción)
    ↓
Agente de Menú Principal
    ↓
Detectar Acción del Agente
    ↓
Router de Acciones
```

---

## SOLUCIÓN 3: Conectar Error Handlers

### Problema
"Global Error Handler" y "AI Error Handler" están desconectados.

### Solución

#### Opción A: Error Handling a Nivel de Workflow (RECOMENDADO)

En n8n, configurar "Error Workflow" a nivel global:

1. Crear workflow separado "Error Handler Workflow"
2. En settings del workflow principal → "Error Workflow" → Seleccionar "Error Handler Workflow"

#### Opción B: Try-Catch en Nodos Críticos

En cada agente AI, envolver con try-catch:

```javascript
try {
  // Código del agente
  const result = await agent.execute();
  return [{ json: result }];
} catch (error) {
  console.error('[Agente Error]', error);

  // Enviar al error handler
  return [{
    json: {
      error: true,
      error_message: error.message,
      error_node: 'Onboarding Agent',
      phone_number: $('Extraer Datos WhatsApp').first().json.phone_number,
      agent_name: 'Onboarding Agent'
    }
  }];
}
```

Luego agregar conexión desde cada agente AI:
- On Error → "AI Error Handler"

#### Opción C: Nodo "Merge" para Errores

1. Crear nodo "Merge" tipo "Wait for Completion"
2. Conectar salidas de error de todos los agentes
3. Merge → "AI Error Handler" → "Enviar Respuesta"

---

## SOLUCIÓN 4: Corregir Detección de Duplicados en Fornecedor

### Problema
El código guarda directamente sin preguntar al usuario.

### Solución

#### A. Modificar "Agente Registrar Fornecedor"

Cambiar el system message para que el agente detecte y reporte duplicados:

```javascript
systemMessage: `📦 Você é Frepi, especialista em cadastrar fornecedores.

🎯 MISSÃO: Cadastrar ou atualizar dados de um fornecedor

DADOS NECESSÁRIOS:
1. Nome do fornecedor
2. Telefone/WhatsApp
3. Dias de entrega
4. Produtos que fornece

IMPORTANTE: Quando tiver todos os dados, SEMPRE verificar duplicados.

FORMATO FINAL (quando tiver TODOS):
FORNECEDOR_DADOS_COMPLETOS
Nome: [nome]
Telefone: [telefone]
Dias: [dias]
Produtos: [produto1, produto2, ...]

TOque: Eficiente. Use emojis: 📦 📞 📅 ✅`
```

#### B. Modificar "Detectar Fornecedor Completo"

Cambiar a buscar "FORNECEDOR_DADOS_COMPLETOS" en lugar de "FORNECEDOR_CADASTRADO":

```javascript
const isComplete = agentOutput.includes('FORNECEDOR_DADOS_COMPLETOS');
```

#### C. Crear nuevo nodo "Buscar Fornecedor Duplicado"

**Tipo:** Code
**Posición:** Después de "Detectar Fornecedor Completo", antes del IF

```javascript
const datos = $input.first().json.dados_fornecedor;
const phoneNumber = $input.first().json.phone_number;

// Buscar fornecedores similares
const { data: existingSuppliers } = await $supabase
  .from('suppliers')
  .select('*')
  .ilike('company_name', `%${datos.nome}%`)
  .limit(5);

const hasDuplicates = existingSuppliers && existingSuppliers.length > 0;

if (hasDuplicates) {
  console.log(`⚠️ Encontrados ${existingSuppliers.length} fornecedores similares`);

  // Generar mensaje para usuario
  let message = `⚠️ *Encontrei fornecedores similares:*\n\n`;
  existingSuppliers.forEach((s, i) => {
    message += `${i + 1}. ${s.company_name}\n`;
    if (s.whatsapp_number) message += `   📞 ${s.whatsapp_number}\n`;
    message += `\n`;
  });

  message += `❓ *O que deseja fazer?*\n\n`;
  message += `1️⃣ Criar novo fornecedor "${datos.nome}"\n`;
  message += `2️⃣ Atualizar um dos existentes\n`;
  message += `3️⃣ Cancelar\n\n`;
  message += `Digite o número da opção.`;

  return [{
    json: {
      duplicate_found: true,
      existing_suppliers: existingSuppliers,
      new_supplier_data: datos,
      phone_number: phoneNumber,
      needs_user_decision: true,
      output: message
    }
  }];
} else {
  // No hay duplicados, proceder a guardar
  return [{
    json: {
      duplicate_found: false,
      dados_fornecedor: datos,
      phone_number: phoneNumber
    }
  }];
}
```

#### D. Modificar "Check If Duplicate"

Cambiar condición a:

```
{{ $json.duplicate_found }} === true
```

Salidas:
- TRUE → Enviar mensaje de alerta → Esperar respuesta → "Handle Duplicate Decision"
- FALSE → "Guardar Fornecedor BD" (simplificado, solo INSERT)

#### E. Simplificar "Guardar Fornecedor BD"

Si no hay duplicados, solo hacer INSERT:

```javascript
const datos = $input.first().json.dados_fornecedor;

// SOLO INSERT, no update
const { data: newSupplier } = await $supabase
  .from('suppliers')
  .insert({
    company_name: datos.nome,
    whatsapp_number: datos.telefone,
    delivery_days: { dias: datos.dias },
    is_active: true
  })
  .select('id')
  .single();

// ... resto del código para vincular productos
```

---

## SOLUCIÓN 5: Reorganizar Nodos

### Posiciones Sugeridas

#### Flujo Principal (Horizontal, Y=800)
```
WhatsApp Trigger         [-1344, 768]
Config Global            [-1120, 768]
Extraer Datos            [-896, 768]
¿Archivo No Soportado?   [-672, 768]
Buscar Usuario           [-448, 768]
¿Usuario Existe?         [-224, 768]
[NUEVO] ¿Es Continuación?  [0, 768]
Calcular % Preferencias  [224, 768]
Verificar Setup          [448, 768]
...
```

#### Flujo de Onboarding (Arriba, Y=200)
```
Crear Nueva Sesión       [0, 200]
Preparar Input           [224, 200]
Onboarding Agent         [448, 200]
Detectar Completo        [800, 200]
¿Completo?               [1088, 200]
...
```

#### Flujo de Compra (Medio, Y=600-700)
```
Crear Sesión Compra      [1824, 700]
Vector Search            [2112, 700]
Agente de Compras        [2400, 700]
Detectar Pedido          [2800, 700]
...
```

#### Flujo de Precios (Arriba, Y=300-400)
```
Preparar Datos           [1824, 350]
Crear Sesión             [2048, 350]
Agente Subir             [2272, 350]
Detectar Completo        [2560, 350]
...
```

#### Flujo de Continuación (Abajo, Y=1200)
```
Detectar Continuação     [2200, 1200]
Router Continuação       [2400, 1200]
...
```

---

## SOLUCIÓN 6: Eliminar Conexiones Duplicadas

### Identificar y Eliminar

#### "Crear Sesión de Compra" - Mantener SOLO:
1. "Router de Acciones" (output 0) ✅
2. "¿Mostrar Menú o Chat?" (output 1) ✅
3. "Router Continuação" (output 0) ✅

Eliminar duplicados de nodos huérfanos.

---

## PLAN DE IMPLEMENTACIÓN

### Fase 1: Correcciones Críticas (2 horas)
1. ✅ Conectar flujo de continuación
2. ✅ Eliminar nodos duplicados
3. ✅ Conectar error handlers (opción B - try-catch)

### Fase 2: Mejoras de Lógica (1 hora)
4. ✅ Corregir detección de duplicados
5. ✅ Eliminar conexiones duplicadas

### Fase 3: Optimización (30 min)
6. ✅ Reorganizar posiciones
7. ✅ Agregar documentación (Sticky Notes)

---

## CHECKLIST DE VERIFICACIÓN

Después de implementar las soluciones:

- [ ] Trigger recibe mensaje ✓
- [ ] Config Global se ejecuta ✓
- [ ] Usuario nuevo → Onboarding completo ✓
- [ ] Usuario existente → Menú principal ✓
- [ ] Hacer compra → Vector search → Agente → Recomendación ✓
- [ ] **Mensaje de continuación → Usuario responde → Detecta continuación ✓**
- [ ] Subir precios → Agente → Guarda en DB ✓
- [ ] Registrar fornecedor → Detecta duplicados → Pregunta → Guarda ✓
- [ ] Error en agente → Captura → Muestra mensaje amigable ✓
- [ ] Setup preferencias → Guarda → Vuelve a menú ✓

---

## CÓDIGO DE PRUEBA

### Test de Continuación

```javascript
// Simular en un nodo de prueba
const phoneNumber = '+5511999999999';

// 1. Marcar sesión como esperando continuación
await $supabase
  .from('line_sessions')
  .update({ awaiting_continuation: true })
  .eq('channel_id', phoneNumber)
  .order('session_end', { ascending: false })
  .limit(1);

console.log('✅ Sesión marcada como esperando continuación');

// 2. Simular mensaje del usuario
const testMessage = {
  phone_number: phoneNumber,
  message: '1' // Hacer outra compra
};

// 3. Verificar que detecta continuación
const { data: session } = await $supabase
  .from('line_sessions')
  .select('*')
  .eq('channel_id', phoneNumber)
  .eq('awaiting_continuation', true)
  .single();

console.log('Sesión encontrada:', session ? 'SÍ ✅' : 'NO ❌');
```

---

*Documento creado: 2025-11-10*
*Versión: 1.0*
