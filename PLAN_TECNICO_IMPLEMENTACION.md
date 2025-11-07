# 🛠️ Plan Técnico de Implementación - Frepi MVP

## 📋 Resumen de Cambios

Basado en tus respuestas, voy a implementar:

1. ✅ **Desbloquear menú** - Acceso sin preferencias obligatorias
2. ✅ **Vuelta al menú** - Pregunta "algo más?" después de cada acción
3. ✅ **Micro-sesiones independientes** - Cada acción tiene su propia sesión
4. ✅ **Advertencia de precios** - Advertir pero permitir continuar
5. ✅ **Indicador de % preferencias** - Visible en menú principal

---

## 📊 FASE 1: Desbloquear Menú (Eliminar Bloqueo de Preferencias)

### Cambio 1.1: Modificar "Verificar Setup Completo"

**Nodo actual**: `Verificar Setup Completo` (Code node)

**Código actual**:
```javascript
const usuario = $input.first().json;

const tienePreferencias = usuario.category_preferences &&
                          Object.keys(usuario.category_preferences).length > 0;

return [{
  json: {
    ...usuario,
    setup_completo: tienePreferencias  // ❌ Bloquea si no tiene
  }
}];
```

**Código nuevo**:
```javascript
const usuario = $input.first().json;

// CAMBIO: Siempre permitir acceso al menú
// Solo calculamos el % de completitud para mostrar
const tienePreferencias = usuario.category_preferences &&
                          Object.keys(usuario.category_preferences).length > 0;

return [{
  json: {
    ...usuario,
    setup_completo: true,  // ✅ SIEMPRE true - menú siempre accesible
    tiene_preferencias: tienePreferencias,  // Flag informativo
    preferencias_porcentaje: usuario.preferencias_porcentaje || 0
  }
}];
```

**Impacto**: Usuario siempre ve el menú después del onboarding.

---

### Cambio 1.2: Actualizar "GENERATE_MAIN_MENU"

**Nodo actual**: `Generar Menú Principal` (Code node)

**Código actual**:
```javascript
const usuario = $input.first().json;
const porcentaje = usuario.preferencias_porcentaje || 0;
const phoneNumber = usuario.phone_number || $input.first().json.phone_number;

const menuText = `🍽️ *Bem-vindo ao Frepi!*

Escolha uma opção:

1️⃣ Fazer uma compra
2️⃣ Atualizar preços de fornecedor
3️⃣ Registrar/Atualizar fornecedor
4️⃣ Configurar preferências (${porcentaje}%)

💬 Você pode digitar o número ou descrever o que precisa.
Exemplo: "quero fazer uma compra" ou "1"`;
```

**Código nuevo**:
```javascript
const usuario = $input.first().json;
const porcentaje = usuario.preferencias_porcentaje || 0;
const phoneNumber = usuario.phone_number || $input.first().json.phone_number;

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
}];
```

**Resultado visual**:
```
🍽️ Bem-vindo ao Frepi!

⚠️ Perfil incompleto (30%)
→ Configure preferências para melhores recomendações!

Escolha uma opção:

1️⃣ Fazer uma compra
2️⃣ Atualizar preços de fornecedor
3️⃣ Registrar/Atualizar fornecedor
4️⃣ Configurar preferências (30%) ⬅️ Recomendado!

💬 Você pode digitar o número ou descrever o que precisa.
```

---

## 📊 FASE 2: Vuelta al Menú (Sistema de Continuación)

### Cambio 2.1: Crear Nodo "Preguntar Continuación"

**Nuevo nodo**: `Preguntar Continuação` (Code node)

```javascript
const input = $input.first().json;
const phoneNumber = input.phone_number;
const usuario = input.user_data || input;

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
}];
```

---

### Cambio 2.2: Crear Nodo "Detectar Opción Continuación"

**Nuevo nodo**: `Detectar Opção Continuação` (Code node)

```javascript
const mensaje = $input.first().json.message.toLowerCase();
const usuario = $input.first().json;

console.log(`🔍 [Continuação] Mensaje: "${mensaje}"`);

// Opción 1: Fazer outra compra
if (mensaje.includes('1') ||
    mensaje.includes('compra') ||
    mensaje.includes('pedido') ||
    mensaje.includes('fazer compra')) {
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
  return [{
    json: {
      ...usuario,
      continuation_action: 'REGISTRAR_FORNECEDOR',
      output_route: 2
    }
  }];
}

// Opción 4: Ver menú principal
if (mensaje.includes('4') ||
    mensaje.includes('menu') ||
    mensaje.includes('voltar') ||
    mensaje.includes('não') ||
    mensaje.includes('nao')) {
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
}];
```

---

### Cambio 2.3: Crear Router de Continuación

**Nuevo nodo**: `Router Continuação` (Switch node)

**Configuración**:
```json
{
  "typeVersion": 3.3,
  "parameters": {
    "mode": "expression",
    "output": "=Output (0): {{ $json.continuation_action === 'FAZER_COMPRA' }}\nOutput (1): {{ $json.continuation_action === 'ATUALIZAR_PRECOS' }}\nOutput (2): {{ $json.continuation_action === 'REGISTRAR_FORNECEDOR' }}\nOutput (3): {{ $json.continuation_action === 'MOSTRAR_MENU' }}"
  }
}
```

**Conexiones**:
- Output 0 → `Crear Sesión de Compra`
- Output 1 → `Preparar Datos Subir Precios`
- Output 2 → `Agente Registrar Fornecedor`
- Output 3 → `GENERATE_MAIN_MENU`

---

### Cambio 2.4: Conectar Flujos Existentes

**Modificar conexiones**:

1. **Después de "Generar Recomendación"**:
   - Antes: `Generar Recomendación` → `Enviar Respuesta` → [FIN]
   - Ahora: `Generar Recomendación` → `Preguntar Continuação` → `Enviar Respuesta`

2. **Después de "Guardar Precios" (cuando precios completos)**:
   - Buscar nodo que envía confirmación de precios guardados
   - Redirigir a: `Preguntar Continuação`

3. **Después de "Guardar Fornecedor"**:
   - Antes: `Guardar Fornecedor BD` → `Check If Duplicate` → `Enviar Respuesta` → [FIN]
   - Ahora: Agregar `Preguntar Continuação` antes de `Enviar Respuesta`

4. **Después de configurar preferencias**:
   - Cuando agente de preferencias termina
   - Redirigir a: `Preguntar Continuação`

---

## 📊 FASE 3: Gestión de Sesiones

### Cambio 3.1: Marcar Sesiones como Completas

**Nuevo nodo**: `Marcar Sessão Completa` (Supabase update)

**Configuración**:
```json
{
  "tableId": "line_sessions",
  "operation": "update",
  "filterType": "manual",
  "matchValue": "={{ $json.session_id }}",
  "fieldsUi": {
    "fieldValues": [
      {
        "fieldId": "session_end",
        "fieldValue": "={{ $now }}"
      },
      {
        "fieldId": "is_completed",
        "fieldValue": "true"
      },
      {
        "fieldId": "last_activity_at",
        "fieldValue": "={{ $now }}"
      }
    ]
  }
}
```

**Conectar ANTES de "Preguntar Continuação"** en todos los flujos:
```
Flujo completo → Marcar Sessão Completa → Preguntar Continuação
```

---

### Cambio 3.2: Verificar que Sesiones Sean Independientes

**Verificar que cada acción crea nueva sesión**:
- ✅ `Crear Sesión de Compra` - Ya existe
- ✅ `Crear Sesión Subir Precios` - Ya existe
- ⚠️ Verificar que `primary_intent` sea único por sesión

**Agregar en cada sesión** el campo `session_data` (JSONB) para guardar contexto:
```javascript
// Ejemplo en Crear Sesión de Compra
{
  "fieldId": "session_data",
  "fieldValue": "={{ { products_requested: [], recommendations_given: [] } }}"
}
```

---

## 📊 FASE 4: Validación de Precios con Advertencias

### Cambio 4.1: Modificar Flujo de Compra

**Insertar validación ANTES de búsqueda de precios**:

```
Agente de Compras (extrae lista)
    ↓
Detectar Pedido Completo
    ↓
[Nuevo] Verificar Disponibilidad de Precios
    ↓
[Nuevo] ¿Precios Actualizados?
    ↓
    ├─ [Sí] → Buscar Proveedores (flujo normal)
    │
    └─ [No] → Mostrar Advertencia → Preguntar Confirmación
              ↓
              ├─ "Sí, continuar" → Buscar Proveedores
              └─ "No, subir precios" → Preparar Datos Subir Precios
```

---

### Cambio 4.2: Crear Nodo "Advertir Precios Desactualizados"

**Nuevo nodo**: `Advertir Preços Desatualizados` (Code node)

```javascript
const input = $input.first().json;
const validacao = input.validacion || [];
const phoneNumber = input.phone_number;

// Construir mensaje de advertencia
let advertencia = `⚠️ *Atenção: Preços Desatualizados*

Alguns produtos não têm preços atualizados nos últimos 30 dias:

`;

// Agregar detalles de productos con precios viejos
const problemasUnicos = validacao.filter(v => v.problema === 'precos_desatualizados');
problemasUnicos.forEach(p => {
  advertencia += `• ${p.produto}: última atualização há ${p.dias_atras} dias\n`;
});

advertencia += `\n💡 As recomendações podem não ser precisas.

Deseja continuar mesmo assim?

1️⃣ Sim, continuar
2️⃣ Não, vou atualizar preços primeiro

Digite o número da opção.`;

return [{
  json: {
    output: advertencia,
    phone_number: phoneNumber,
    user_data: input,
    awaiting_price_confirmation: true,
    productos_solicitados: input.productos
  }
}];
```

---

### Cambio 4.3: Modificar "Generar Recomendación"

**Agregar nota al final si hay precios desactualizados**:

```javascript
// Al final del mensaje de recomendación, si hay problemas
if (hayProblemas) {
  mensaje += `\n\n⚠️ *Nota*: Alguns preços estão desatualizados.
Recomendo atualizar seus preços para recomendações mais precisas.`;
}
```

---

## 📊 FASE 5: Mejoras en Prompts (Empleado Útil)

### Cambio 5.1: Actualizar Prompt de "Agente de Compras"

**Agregar al inicio del system message**:

```
🎯 VOCÊ É: Um assistente de procurement dedicado, como um funcionário experiente
ajudando seu chefe a fazer as melhores compras.

SUA ATITUDE:
- Proativo: Sugira produtos relacionados que podem estar faltando
- Atento: Lembre do histórico de compras anteriores
- Consultivo: Explique POR QUÊ está recomendando cada fornecedor
- Eficiente: Vá direto ao ponto, sem ser robótico
```

---

### Cambio 5.2: Actualizar Prompt de "Agente Subir Precios"

**Agregar**:

```
💡 DICA PROATIVA: Se o usuário enviar apenas 2-3 produtos, pergunte:
"Vi que você enviou preços de [produtos]. Tem mais produtos desse fornecedor
que gostaria de cadastrar agora?"
```

---

### Cambio 5.3: Actualizar Prompt de "Agente Registrar Fornecedor"

**Agregar**:

```
💡 SEJA CONSULTIVO: Quando o usuário registrar um fornecedor, pergunte:
"Ótimo! Já tem os preços deste fornecedor para cadastrar também?"

Se sim → Sugerir "Vamos cadastrar os preços agora?"
```

---

## 📊 Diagrama del Flujo Completo Nuevo

```
[WhatsApp Message]
    ↓
Extraer Datos
    ↓
¿Usuario Existe?
    ↓
   [Sí]
    ↓
Verificar Setup Completo (MODIFICADO - siempre true)
    ↓
¿Es mensaje de continuación? (NUEVO)
    ↓
    ├─ [No] → GENERATE_MAIN_MENU (MODIFICADO - con advertencias)
    │            ↓
    │         Detectar Opción del Menú
    │            ↓
    │         Router de Acciones
    │            ↓
    │         ┌──┴──┬─────────┬──────────┐
    │         ↓     ↓         ↓          ↓
    │      Compra  Preços  Fornecedor  Config
    │         ↓     ↓         ↓          ↓
    │     [Ejecuta acción...]
    │         ↓     ↓         ↓          ↓
    │    Marcar Sessão Completa (NUEVO)
    │         ↓     ↓         ↓          ↓
    │    Preguntar Continuação (NUEVO)
    │         ↓
    │    Enviar Respuesta
    │         ↓
    │    [Usuario responde]
    │         ↓
    └────────┘

    ├─ [Sí] → Detectar Opção Continuação (NUEVO)
                 ↓
              Router Continuação (NUEVO)
                 ↓
              ┌──┴──┬──────┬────────┐
              ↓     ↓      ↓        ↓
           Compra Preços Fornec. Menu
```

---

## 📊 Resumen de Nodos Nuevos

| Nodo | Tipo | Función |
|------|------|---------|
| `Preguntar Continuação` | Code | Genera mensaje "¿algo más?" |
| `Detectar Opção Continuação` | Code | Detecta qué quiere hacer el usuario |
| `Router Continuação` | Switch | Rutea a la acción elegida o menú |
| `Marcar Sessão Completa` | Supabase | Marca sesión como finalizada |
| `Advertir Preços Desatualizados` | Code | Muestra advertencia de precios viejos |
| `Router Confirmação Preços` | Switch | Rutea según confirmación del usuario |

**Total nodos nuevos**: 6
**Total nodos modificados**: 8
**Workflow final**: ~94 nodos (88 actuales + 6 nuevos)

---

## 📊 Conexiones Críticas a Modificar

### 1. Flujo de Compra
```
ANTES:
Generar Recomendación → Enviar Respuesta → [FIN]

DESPUÉS:
Generar Recomendación → Marcar Sessão Completa → Preguntar Continuação → Enviar Respuesta → [Espera respuesta usuario] → Detectar Opção Continuação → Router Continuação
```

### 2. Flujo de Subir Precios
```
ANTES:
Guardar Precios → Enviar Confirmación → [FIN]

DESPUÉS:
Guardar Precios → Marcar Sessão Completa → Preguntar Continuação → Enviar Respuesta → [Espera] → Detectar → Router
```

### 3. Flujo de Fornecedor
```
ANTES:
Guardar Fornecedor → Check Duplicate → Enviar Respuesta → [FIN]

DESPUÉS:
Guardar Fornecedor → Check Duplicate → Marcar Sessão → Preguntar Continuação → Enviar → [Espera] → Detectar → Router
```

---

## ✅ Checklist de Validación

Antes de ejecutar, verificaré:

- [ ] Todos los prompts en portugués brasileiro
- [ ] Mensajes naturales y útiles (no robóticos)
- [ ] Cada sesión es independiente
- [ ] No se rompen flujos existentes
- [ ] Switch nodes usan typeVersion 3.3 con expression mode
- [ ] Conexiones usan nombres de nodos (no IDs)
- [ ] JSON válido para importar en n8n
- [ ] Lógica de lenguaje natural funciona
- [ ] Emojis apropiados en todos los mensajes

---

## 🎯 Pregunta Final

**¿Apruebas este plan técnico?**

Puntos específicos a confirmar:

1. ✅ **Flujo de continuación** - ¿Te parece bien la estructura de 4 opciones después de cada acción?

2. ✅ **Advertencia de precios** - ¿Está bien mostrarla solo cuando hay precios > 30 días, y permitir continuar?

3. ✅ **Mensajes del menú** - ¿Te gusta cómo se ve el menú con la advertencia de perfil incompleto?

4. ✅ **Sesiones independientes** - ¿Está claro que cada compra/precio/fornecedor crea su propia sesión que se cierra al terminar?

5. ✅ **Tono "empleado útil"** - ¿Los prompts actualizados suenan como un empleado de procurement proactivo?

**Si todo está bien, responde "Aprobado" y comenzaré la implementación en el orden de las fases.**

Si necesitas ajustar algo, dime qué y lo modifico en el plan antes de tocar código. 🚀
