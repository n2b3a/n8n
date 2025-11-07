# 🍽️ Frepi - Asistente de Compras por WhatsApp

## 📋 ¿Qué es Frepi?

**Frepi** es un asistente conversacional de WhatsApp que ayuda a restaurantes brasileños a:
- 📝 Gestionar listas de productos y proveedores
- 💰 Comparar precios entre diferentes proveedores
- 🛒 Recibir recomendaciones inteligentes de compra
- ⚙️ Configurar preferencias de compra personalizadas

**Idioma**: 100% Portugués Brasileiro

---

## 🎯 ¿Qué Hace?

### Funcionalidades Principales

1. **Registro y Onboarding**
   - Recolecta datos del restaurante (nombre, contacto, ciudad, tipo)
   - Guía al usuario paso a paso en configuración inicial
   - Calcula % de completitud del perfil

2. **Gestión de Precios**
   - Recibe listas de precios por texto (formato libre o estructurado)
   - Usa embeddings para identificar productos similares
   - Almacena histórico de precios por proveedor

3. **Registro de Proveedores**
   - Captura: nombre, teléfono, días de entrega, productos
   - **Detecta duplicados** y ofrece opciones (nuevo/actualizar/cancelar)
   - Vincula productos con proveedores

4. **Recomendaciones de Compra**
   - Compara precios entre proveedores
   - Considera preferencias del restaurante
   - **Score inteligente** basado en precio + calidad
   - ⚠️ **Solo recomienda** - NO envía pedidos automáticamente

5. **Configuración de Preferencias**
   - Productos frecuentes
   - Proveedores preferidos
   - Frecuencia de compras
   - Orçamento mensal
   - Condições de pagamento

---

## 🏗️ Estructura del Workflow

### Componentes Principales (88 nodos)

```
WhatsApp Trigger (entrada)
    ↓
Extraer Datos del Mensaje
    ↓
┌─────────────────────────────┐
│  ¿Usuario Existe?           │
└─────────────────────────────┘
    ↓                    ↓
   [No]                [Sí]
    ↓                    ↓
Onboarding          ¿Setup Completo?
Agent                   ↓
    ↓              ┌────┴────┐
Guardar          [Sí]      [No]
Datos              ↓         ↓
    ↓          Menú      Configuración
    └──────────┘       Pendiente
                          ↓
                   MENÚ PRINCIPAL
                 ┌──────┴──────┐
        ┌────────┼────────┬────┴────┐
        ↓        ↓        ↓         ↓
    Compra   Precios  Fornecedor  Config
```

### Agentes AI (4 totales)

| Agente | Función | Motor |
|--------|---------|-------|
| **Onboarding Agent** | Registro inicial del restaurante | GPT-4.1-mini |
| **Agente de Compras** | Procesa pedidos y recomienda | GPT-4.1-mini |
| **Agente Subir Precios** | Extrae precios de texto libre | GPT-4.1-mini |
| **Agente Registrar Fornecedor** | Captura datos de proveedores | GPT-4.1-mini |

### Base de Datos (Supabase)

**Tablas principales**:
- `restaurants` - Datos del restaurante
- `restaurant_people` - Personas de contacto
- `suppliers` - Proveedores
- `master_list` - Catálogo de productos
- `pricing_history` - Histórico de precios
- `supplier_mapped_products` - Productos por proveedor
- `line_sessions` - Sesiones de conversación

---

## 💬 Cómo Usar el Bot (Usuario Final)

### Primera Vez - Onboarding

```
Usuario: [Cualquier mensaje]

Frepi: "Olá! Prazer em te conhecer! 😊
       Sou o Frepi, seu assistente de compras.

       Antes de começar, vou precisar de algumas informações básicas.
       Qual é o nome do seu restaurante?"

Usuario: "Restaurante da Vila"

Frepi: "Ótimo! Qual é o nome da pessoa de contato?"

Usuario: "João Silva"

Frepi: "Em que cidade fica o restaurante?"

Usuario: "São Paulo"

Frepi: "Que tipo de negócio é?"

Usuario: "Restaurante italiano"

Frepi: "✅ Perfeito! Cadastro completo!
       Agora você pode usar o Frepi. Digite 'menu' para ver as opções."
```

### Menú Principal

```
Usuario: "menu"  (o "quero fazer uma compra")

Frepi: "🍽️ Bem-vindo ao Frepi!

       Escolha uma opção:

       1️⃣ Fazer uma compra
       2️⃣ Atualizar preços de fornecedor
       3️⃣ Registrar/Atualizar fornecedor
       4️⃣ Configurar preferências (30%)

       💬 Você pode digitar o número ou descrever o que precisa.
       Exemplo: 'quero fazer uma compra' ou '1'"
```

### Opción 1: Fazer uma Compra

```
Usuario: "1"  (o "quero fazer uma compra")

Frepi: "🛒 Perfeito! Qual é a sua lista de compras?"

Usuario: "preciso de 5kg de arroz e 3 litros de óleo"

Frepi: [Busca en catálogo con embeddings]
       [Compara precios entre proveedores]
       [Calcula scores]

       "📊 Recomendação de compra:

       🍚 Arroz Integral (5kg)
         • Fornecedor ABC: R$ 25.50 ⭐ (preferido)
         • Fornecedor XYZ: R$ 23.00

       🛢️ Óleo de Soja (3L)
         • Fornecedor ABC: R$ 18.00 ⭐
         • Fornecedor XYZ: R$ 19.50

       💰 Total melhor opção: R$ 43.50 (ABC)

       ━━━━━━━━━━━━━━━━━━━━━━
       💡 IMPORTANTE
       Esta é uma recomendação para te ajudar a decidir.
       Você precisa fazer o pedido diretamente com os fornecedores.
       Frepi NÃO envia pedidos automaticamente."
```

### Opción 2: Atualizar Preços

```
Usuario: "2"  (o "atualizar preços")

Frepi: "💰 Envie a lista de preços do seu fornecedor.

       Pode ser em formato livre:
       'Leite 4.50/L
        Arroz 5.20/kg'

       Ou estruturado:
       'Fornecedor: Piracanjuba
        - Leite 4.50/L
        - Queijo 18.00/kg'"

Usuario: "Fornecedor: Mercadão
         - Arroz Tio João 5.20/kg
         - Feijão Preto 4.80/kg"

Frepi: [Extrae con AI]
       [Valida con embeddings]
       [Guarda en pricing_history]

       "✅ Preços cadastrados com sucesso!

       2 produtos atualizados:
       • Arroz Tio João - R$ 5.20/kg
       • Feijão Preto - R$ 4.80/kg

       Fornecedor: Mercadão"
```

### Opción 3: Registrar Fornecedor

```
Usuario: "3"  (o "registrar fornecedor")

Frepi: "📦 Vou te ajudar a cadastrar um fornecedor.
       Qual é o nome?"

Usuario: "Distribuidora Central"

Frepi: [Busca duplicados]

       "⚠️ Já existe um fornecedor cadastrado: Distribuidora Central (11-98765-4321)

       Deseja:
       1️⃣ Criar novo fornecedor mesmo assim
       2️⃣ Atualizar dados do existente
       3️⃣ Cancelar"

Usuario: "2"

Frepi: "Qual é o telefone/WhatsApp?"

Usuario: "11-91234-5678"

Frepi: "Quais são os dias de entrega?"

Usuario: "Segunda, quarta e sexta"

Frepi: "Quais produtos esse fornecedor oferece?"

Usuario: "arroz, feijão, óleo, açúcar"

Frepi: "✅ Fornecedor atualizado com sucesso!

       📦 Distribuidora Central
       📞 11-91234-5678
       📅 Entrega: Segunda, quarta e sexta
       📦 4 produto(s) vinculado(s)"
```

### Opción 4: Configurar Preferências

```
Usuario: "4"  (o "configurar preferências")

Frepi: "⚙️ PREFERÊNCIAS (30% completo)

       Escolha o que deseja configurar:

       1️⃣ Produtos frequentes
       2️⃣ Fornecedores preferidos
       3️⃣ Frequência de compras
       4️⃣ Orçamento mensal
       5️⃣ Condições de pagamento
       6️⃣ Voltar ao menu principal"

Usuario: "1"  (o "produtos frequentes")

Frepi: "📦 Quais categorias de produtos você compra com mais frequência?"

Usuario: "grãos, óleos, laticínios"

Frepi: "✅ Preferências atualizadas! (40% completo)"
```

---

## 🧠 Inteligencia del Sistema

### 1. Detección de Lenguaje Natural

**Antes**: Solo números (1, 2, 3, 4)
**Ahora**: Frases naturales en portugués

| Usuario Escribe | Sistema Detecta |
|-----------------|-----------------|
| "quero fazer uma compra" | Opción 1 - Compra |
| "preciso atualizar preços" | Opción 2 - Precios |
| "cadastrar fornecedor" | Opción 3 - Fornecedor |
| "ver preferências" | Opción 4 - Config |

### 2. Matching de Productos (Vector Embeddings)

```
Usuario: "preciso de leite"
Sistema:
  1. Genera embedding del texto
  2. Busca en master_list por similitud
  3. Encuentra: "Leite Integral", "Leite Desnatado", etc.
  4. Muestra opciones al usuario
```

### 3. Score de Recomendación

```javascript
// Fórmula del score
final_score = (price_score × (1 - price_sensitivity)) +
              (preferred_bonus × price_sensitivity)

Donde:
- price_score: 0-1 (precio normalizado, invertido)
- price_sensitivity: 0.2-0.8 (del perfil del restaurante)
- preferred_bonus: +0.2 si es proveedor preferido
```

**Ejemplo**:
- Restaurante con `price_sensitivity = 0.7` (prioriza calidad)
- Proveedor preferido con precio 10% más alto
- **Gana el proveedor preferido** por el bonus de calidad

### 4. Validación de Precios

Antes de recomendar, verifica:
- ✅ Precio existe en últimos 30 días
- ⚠️ Si > 30 días: muestra advertencia pero permite continuar
- ❌ Si no existe: sugiere actualizar precios

---

## 📊 Flujo de Datos

```
WhatsApp Message
    ↓
Extracción de datos (texto/archivo)
    ↓
Verificación de usuario → BD: restaurants
    ↓
Sesión activa? → BD: line_sessions
    ↓
Router de acciones
    ↓
┌───────────┬─────────────┬──────────────┬──────────┐
↓           ↓             ↓              ↓          ↓
Compra    Precios    Fornecedor    Config     Menú
    ↓           ↓             ↓              ↓
Vector    Parsing      Duplicate       Update
Search      AI          Check       Preferences
    ↓           ↓             ↓              ↓
Compare   Save to      Save to        Save to
Suppliers pricing_h.  suppliers    restaurants
    ↓           ↓             ↓              ↓
Score     Confirm       Confirm        Show %
Ranking                                Complete
    ↓
Recommend
    ↓
WhatsApp Response
```

---

## 🔑 Características Clave

### ✅ Lo que Frepi HACE

- ✅ Registra restaurantes y usuarios
- ✅ Gestiona catálogo de productos
- ✅ Rastrea precios de múltiples proveedores
- ✅ Compara precios inteligentemente
- ✅ **Recomienda** las mejores opciones de compra
- ✅ Guarda histórico de precios
- ✅ Detecta y previene duplicados
- ✅ Entiende lenguaje natural (no solo números)
- ✅ Usa AI para extraer datos de texto libre

### ❌ Lo que Frepi NO HACE

- ❌ **NO envía pedidos automáticamente a proveedores**
- ❌ NO procesa pagos
- ❌ NO hace entregas
- ❌ NO gestiona inventario actual
- ❌ NO procesa imágenes (todavía)

### 🔮 Futuro (Backlog)

- 📸 OCR para fotos de facturas
- 📦 Seguimiento de pedidos
- 📊 Dashboard de analytics
- 📈 Predicción de necesidades
- 🤝 Integración directa con proveedores

---

## 🎨 Diseño de Conversación

### Principios

1. **Natural, no robótico** - Como un amigo que ayuda
2. **Emojis apropiados** - Visual y amigable
3. **Respuestas cortas** - Máximo 2-3 líneas por interacción
4. **Feedback constante** - Usuario siempre sabe dónde está
5. **Portugués brasileiro** - Adaptado culturalmente

### Tono de Voz

```
❌ Mal: "Solicitud procesada exitosamente. ID: 12345"
✅ Bien: "✅ Perfeito! Preços cadastrados com sucesso!"

❌ Mal: "Error: campo requerido faltante"
✅ Bien: "Ops! 😅 Qual é o telefone do fornecedor?"

❌ Mal: "Iniciando proceso de onboarding..."
✅ Bien: "Olá! Prazer em te conhecer! 😊"
```

---

## 📱 Acceso a Funcionalidades

### Para Usuarios Finales (Restaurantes)

1. **Primer acceso**: Enviar cualquier mensaje al número de WhatsApp
2. **Onboarding automático**: Sistema guía registro
3. **Menú siempre disponible**: Escribir "menu" en cualquier momento
4. **Navegación natural**: Usar frases o números

### Para Administradores

1. **n8n Dashboard**: Ver ejecuciones y logs
2. **Supabase**: Acceso directo a datos
3. **OpenAI**: Monitor de uso de tokens
4. **WhatsApp Business**: Gestión de cuenta

### Endpoints Clave

- **Webhook**: `/webhook/whatsapp` - Recibe mensajes
- **Supabase URL**: Configurado en credenciales
- **OpenAI API**: Configurado en credenciales

---

## 📈 Métricas y Monitoreo

### KPIs del Sistema

- **% de Setup completo** por restaurante (5 campos)
- **Tiempo de respuesta** promedio
- **Tasa de conversión** onboarding → usuario activo
- **Número de precios** actualizados por semana
- **Número de comparaciones** de compra realizadas

### Logs Importantes

```javascript
console.log('🔍 [Detectar Opción] Mensaje recibido: "..."')
console.log('✅ [Vector Search] Encontrados 3 productos similares')
console.log('⚠️ [Salvar Fornecedor] 2 fornecedor(es) similar(es) encontrado(s)')
console.log('💰 [Score] Proveedor ABC: 0.85, XYZ: 0.72')
```

---

## 🛠️ Soporte Técnico

### Estructura de Archivos

```
n8n/
├── workflow-frepi-mvp1-mejorado.json   ← Workflow principal (88 nodos)
├── COMO_IMPORTAR.md                     ← Guía de importación
├── CHANGES_SUMMARY.md                   ← Detalles técnicos
├── validate_workflow.py                 ← Validación de estructura
├── fix_connections.py                   ← Fix de conexiones
├── fix_switch_nodes.py                  ← Fix de Switch nodes
└── deep_validate.py                     ← Inspección profunda
```

### Solución de Problemas Comunes

| Problema | Causa | Solución |
|----------|-------|----------|
| Bot no responde | Workflow inactivo | Activar en n8n |
| Respuestas en español | Prompt incorrecto | Verificar systemMessage |
| Precios no se guardan | Credenciales Supabase | Revisar conexión DB |
| Productos no se encuentran | Catálogo vacío | Poblar master_list |
| Score incorrecto | price_sensitivity mal | Verificar valor 0.2-0.8 |

---

## 🎯 Resumen Ejecutivo

**Frepi** es un chatbot de WhatsApp que ayuda a restaurantes brasileños a optimizar sus compras mediante:

- 🤖 **Conversación natural** con AI (GPT-4.1-mini)
- 💰 **Comparación inteligente** de precios entre proveedores
- 📊 **Recomendaciones basadas en datos** históricos y preferencias
- 🔄 **Gestión simplificada** de catálogos y proveedores
- 📱 **Accesible desde WhatsApp** - sin apps adicionales

**Tecnologías**: n8n, OpenAI, Supabase, Vector Embeddings, WhatsApp Business API

**Estado actual**: MVP funcional con 88 nodos, listo para testing en producción.

---

**Versión del documento**: 1.0
**Última actualización**: 2025-11-06
**Commit**: 6ab4d28
