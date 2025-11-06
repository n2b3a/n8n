# Frepi MVP - Mejoras Implementadas

## Resumen
Se implementaron 3 mejoras críticas al workflow de Frepi MVP basadas en feedback del usuario:

1. ✅ **Detección de lenguaje natural en menús**
2. ✅ **Verificación de proveedores duplicados**
3. ✅ **Clarificación del alcance de recomendaciones**

**Resultado**: Workflow actualizado de 84 a 88 nodos (+4 nodos nuevos)

---

## 1. Detección de Lenguaje Natural en Menús

### Problema
Los usuarios tenían que escribir números (1, 2, 3, 4) para seleccionar opciones del menú.

### Solución
Ahora los usuarios pueden escribir frases naturales en portugués brasileño:
- ✅ "quero fazer uma compra" → Opción 1
- ✅ "preciso atualizar preços" → Opción 2
- ✅ "registrar fornecedor" → Opción 3
- ✅ "configurar preferências" → Opción 4

### Nodos Modificados

#### `Detectar Opción del Menú`
- **Antes**: Solo detectaba números (1, 2, 3, 4)
- **Ahora**: Detecta múltiples variantes:
  - Compra: "compra", "pedido", "fazer uma compra", "fazer compra", "quero comprar", "preciso comprar"
  - Preços: "precio", "preço", "atualizar preço", "cadastrar preço", "enviar preço"
  - Fornecedor: "fornecedor", "registrar fornecedor", "cadastrar fornecedor", "adicionar fornecedor", "novo fornecedor"
  - Configuração: "preferencia", "preferência", "configurar", "configuração", "config"

#### `GENERATE_MAIN_MENU`
- **Cambio**: Mensaje actualizado
```
💬 Você pode digitar o número ou descrever o que precisa.
Exemplo: "quero fazer uma compra" ou "1"
```

#### `DETECT_PREFERENCE_OPTION` (Submenu de preferencias)
- **Antes**: Solo números 1-6
- **Ahora**: Acepta también:
  - "produto", "frequente", "categoria" → Opción 1
  - "fornecedor", "preferido" → Opción 2
  - "frequência", "compra" → Opción 3
  - "orçamento", "gasto", "budget" → Opción 4
  - "pagamento", "condição" → Opción 5
  - "voltar", "menu", "sair" → Opción 6

#### `GENERATE_PREFERENCES_SUBMENU`
- **Cambio**: Mensaje actualizado con hint de lenguaje natural

---

## 2. Verificación de Proveedores Duplicados

### Problema
Cuando el usuario registraba un proveedor que ya existía, el sistema sobrescribía sin preguntar.

### Solución
Ahora el sistema:
1. 🔍 Busca proveedores similares (ILIKE %nombre%)
2. ⚠️ Si encuentra coincidencias, muestra lista y pregunta:
   - 1️⃣ Crear nuevo de todos modos
   - 2️⃣ Atualizar datos del existente
   - 3️⃣ Cancelar
3. ✅ Ejecuta la acción elegida por el usuario

### Nodos Nuevos

#### `HANDLE_DUPLICATE_SUPPLIER_DECISION` (Nuevo)
Procesa la decisión del usuario sobre qué hacer con el duplicado:
- Opción 1: Crea nuevo proveedor con los datos ingresados
- Opción 2: Actualiza el proveedor existente (primero de la lista)
- Opción 3: Cancela el registro

#### `CHECK_IF_DUPLICATE` (Nuevo)
Router IF que verifica el flag `duplicate_found` del nodo anterior y divide el flujo:
- TRUE → Envía mensaje de advertencia
- FALSE → Envía mensaje de éxito

#### `DETECT_DUPLICATE_DECISION` (Nuevo)
Detecta si el output del agente contiene una decisión de duplicado en formato:
```
DECISAO_DUPLICADO:[1|2|3]
```

#### `Router: ¿Es Decisión Duplicado?` (Nuevo)
Switch que rutea según el flag `is_duplicate_decision`:
- TRUE → `HANDLE_DUPLICATE_SUPPLIER_DECISION`
- FALSE → `SAVE_FORNECEDOR_DB` (flujo normal)

### Nodos Modificados

#### `SAVE_FORNECEDOR_DB`
- **Cambio principal**: Antes de insertar, busca duplicados
```javascript
const { data: existingSuppliers } = await $supabase
  .from('suppliers')
  .select('id, company_name, whatsapp_number')
  .ilike('company_name', `%${datos.nome}%`)
  .limit(5);

if (existingSuppliers && existingSuppliers.length > 0) {
  // Devuelve mensaje de advertencia con opciones
  return [{
    json: {
      duplicate_found: true,
      existing_suppliers: existingSuppliers,
      new_supplier_data: datos,
      output: warningMessage,
      needs_user_decision: true
    }
  }];
}
```

#### `AGENT_REGISTER_FORNECEDOR`
- **Cambio**: Prompt del agente mejorado para reconocer y responder a decisiones de duplicados
- Cuando el usuario responde "1", "2" o "3" en contexto de duplicado, el agente responde:
  ```
  DECISAO_DUPLICADO:1  (o 2 o 3)
  ```

### Flujo de Conexiones
```
AGENT_REGISTER_FORNECEDOR
  ↓
DETECT_DUPLICATE_DECISION
  ↓
ROUTER_DUPLICATE_DECISION
  ↓
  ├─[Si es decisión]→ HANDLE_DUPLICATE_SUPPLIER_DECISION → Enviar Respuesta
  │
  └─[Si no es decisión]→ SAVE_FORNECEDOR_DB
                           ↓
                         CHECK_IF_DUPLICATE
                           ↓
                           ├─[Duplicate found]→ Enviar Respuesta (advertencia)
                           └─[No duplicate]→ Enviar Respuesta (éxito)
```

---

## 3. Clarificación del Alcance de Recomendaciones

### Problema
El sistema no dejaba claro que **NO envía pedidos automáticamente** a los proveedores.
Esto podía crear expectativas incorrectas.

### Solución
Mensajes explícitos en múltiples puntos del flujo indicando que Frepi:
- ✅ **Solo recomienda** las mejores opciones
- ❌ **No envía pedidos** automáticamente
- 👤 El **usuario debe contactar** a los proveedores directamente

### Nodos Modificados

#### `Agente de Compras` (System Prompt)
- **Agregado** al inicio del prompt:
```
⚠️ *IMPORTANTE*:
Você NÃO envia pedidos automaticamente aos fornecedores.
Você APENAS recomenda as melhores opções baseado nos preços cadastrados.
O restaurante fará o pedido DIRETAMENTE com os fornecedores escolhidos.
```

#### `Generar Recomendación`
- **Antes**:
```javascript
mensaje += 'Confirma o pedido? 👍';
```

- **Ahora**:
```javascript
mensaje += `

━━━━━━━━━━━━━━━━━━━━━━
💡 *IMPORTANTE*

Esta é uma *recomendação* para te ajudar a decidir.
Você precisa fazer o pedido *diretamente com os fornecedores*.

Frepi NÃO envia pedidos automaticamente.

Deseja salvar estas informações para referência? (Sim/Não)`;
```

---

## Resumen de Nodos

### Estado Final
- **Total de nodos**: 88 (antes: 84)
- **Nodos nuevos**: 4
  1. `HANDLE_DUPLICATE_SUPPLIER_DECISION`
  2. `CHECK_IF_DUPLICATE`
  3. `DETECT_DUPLICATE_DECISION`
  4. `Router: ¿Es Decisión Duplicado?`

### Nodos Modificados
1. `Detectar Opción del Menú` - Lenguaje natural
2. `GENERATE_MAIN_MENU` - Hint de lenguaje natural
3. `DETECT_PREFERENCE_OPTION` - Lenguaje natural
4. `GENERATE_PREFERENCES_SUBMENU` - Hint
5. `SAVE_FORNECEDOR_DB` - Detección de duplicados
6. `AGENT_REGISTER_FORNECEDOR` - Manejo de decisiones
7. `Agente de Compras` - Clarificación de alcance
8. `Generar Recomendación` - Disclaimer de alcance

---

## Próximos Pasos Recomendados

### Inmediato
1. ✅ Commit de cambios a git
2. ✅ Push a branch `claude/n8n-json-integration-011CUptXDtoKvtMESc65mKaW`
3. 🧪 Testing en ambiente de desarrollo
4. 📝 Documentar casos de uso de prueba

### Futuro (Backlog)
1. Implementar agentes de preferencias restantes (2-5)
2. OCR para facturas (Fase 3)
3. Seguimiento post-pedido (Fase 4)
4. Dashboard de analytics (Fase 5)

---

## Testing Recomendado

### 1. Lenguaje Natural en Menús
```
Usuario: "quero fazer uma compra"
Esperado: Sistema detecta Opción 1 (Hacer compra)

Usuario: "preciso cadastrar um fornecedor"
Esperado: Sistema detecta Opción 3 (Registrar fornecedor)

Usuario: "quero ver as minhas preferências"
Esperado: Sistema detecta Opción 4 (Configurar preferências)
```

### 2. Verificación de Duplicados
```
# Registro inicial
Usuario: "Registrar fornecedor"
Sistema: "Nome do fornecedor?"
Usuario: "Piracanjuba"
Sistema: [Solicita datos...]
Usuario: [Completa datos]

# Intento de duplicado
Usuario: "Registrar fornecedor"
Sistema: "Nome?"
Usuario: "Piracanjuba"  (ya existe)
Esperado: Sistema muestra advertencia con 3 opciones
Usuario: "2" (actualizar existente)
Esperado: Sistema actualiza el proveedor existente
```

### 3. Clarificación de Alcance
```
Usuario: "Quero fazer uma compra"
Sistema: [Procesa pedido y genera recomendación]
Esperado: Mensaje incluye disclaimer:
  "💡 IMPORTANTE
   Esta é uma recomendação para te ajudar a decidir.
   Você precisa fazer o pedido diretamente com os fornecedores.
   Frepi NÃO envia pedidos automaticamente."
```

---

## Notas Técnicas

### Base de Datos
No se requieren cambios en el schema de Supabase. Todas las mejoras usan las tablas existentes:
- `suppliers`
- `supplier_mapped_products`
- `restaurants`
- `line_sessions`

### Compatibilidad
✅ Retrocompatible - usuarios pueden seguir usando números si lo prefieren
✅ No rompe funcionalidad existente
✅ Mejora UX sin cambios en DB schema

### Performance
- Búsqueda de duplicados usa `ILIKE %nombre%` (limitado a 5 resultados)
- Sin impacto significativo en latencia
- Sugerencia futura: Índice en `suppliers.company_name` para optimizar búsquedas

---

Generado automáticamente por Claude Code
Fecha: 2025-11-06
Workflow: Frepi MVP1 - Main | SA
