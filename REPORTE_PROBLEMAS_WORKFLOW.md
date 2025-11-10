# 🔴 REPORTE DE PROBLEMAS - Workflow Frepi MVP1

## Fecha de Análisis
2025-11-10

## Resumen Ejecutivo
Se encontraron **PROBLEMAS CRÍTICOS** en el workflow que impiden su correcto funcionamiento. Se identificaron nodos desconectados, flujos rotos y referencias inconsistentes.

---

## 1. NODOS COMPLETAMENTE DESCONECTADOS (HUÉRFANOS)

### 🔴 CRÍTICO: Flujo de Continuación Roto

#### Nodo: "¿Es Interacción de Menú?"
- **ID:** `d88ea515-57c8-492a-9a59-8103072a6d0c`
- **Problema:** No tiene conexión de entrada
- **Posición:** [0, 1776]
- **Impacto:** El usuario nunca llega a este nodo, el flujo de interacción con el menú está roto
- **Salidas configuradas:**
  - TRUE → "Detectar Opción del Menú"
  - FALSE → "Enviar Respuesta"

#### Nodo: "Detectar Opção Continuação"
- **ID:** `DETECTAR_OPCAO_CONTINUACAO`
- **Problema:** No tiene conexión de entrada
- **Posición:** [2200, 2928]
- **Impacto:** El flujo de continuación después de completar una acción no funciona
- **Salidas configuradas:** Va a "Router Continuação"

#### Nodo: "Router de Opciones"
- **ID:** `40156080-5c02-4d4b-aa6b-f9f4fbeb309f`
- **Problema:** No tiene conexión de entrada
- **Posición:** [512, 1840]
- **Impacto:** Las opciones del menú no se pueden enrutar correctamente
- **Salidas configuradas:**
  - Output 0 → "Preparar Datos Subir Precios"
  - Output 1 → "Crear Sesión de Compra" (DUPLICADO - ya existe otra conexión)
  - Output 2 → "Mensaje Configurações"
  - Output 3 → "¿Mostrar Menú o Chat?"

### 🟡 ADVERTENCIA: Nodos de Manejo de Errores Desconectados

#### Nodo: "Global Error Handler"
- **ID:** `GLOBAL_ERROR_HANDLER`
- **Problema:** No tiene conexión de entrada
- **Posición:** [2400, 3728]
- **Impacto:** Los errores globales no se capturan
- **Salida:** Va a "Enviar Respuesta"

#### Nodo: "AI Error Handler"
- **ID:** `AI_ERROR_HANDLER`
- **Problema:** No tiene conexión de entrada
- **Posición:** [2600, 3928]
- **Impacto:** Los errores de agentes AI no tienen fallback
- **Salida:** Va a "Enviar Respuesta"

---

## 2. FLUJOS ROTOS Y DESCONECTADOS

### 🔴 CRÍTICO: Ciclo de Continuación Incompleto

**Problema Principal:**
El workflow muestra mensajes de continuación al usuario pero no captura las respuestas.

**Flujo Actual (ROTO):**
```
Completion Handler → Update Session DB → Enviar Respuesta
                                              ↓
                                         (USUARIO RESPONDE)
                                              ↓
                                         ??? (NADA) ???
```

**Nodos Afectados:**
- "Detectar Opção Continuação" está huérfano
- "Router Continuação" no recibe datos
- El mensaje de continuación se envía pero la respuesta no se procesa

**Flujo Esperado (CORRECTO):**
```
Completion Handler → Update Session DB → Enviar Respuesta
                                              ↓
                                     WhatsApp Trigger (nueva interacción)
                                              ↓
                                     Detectar si es continuación
                                              ↓
                                     Detectar Opção Continuação
                                              ↓
                                     Router Continuação
```

### 🔴 CRÍTICO: Flujo de Menú Desconectado

**Problema:**
El nodo "Generar Menú Principal" tiene múltiples entradas pero el flujo principal no conecta correctamente con él.

**Flujo Actual:**
```
Calcular % Preferencias → Verificar Setup Completo → ¿Setup Completo?
                                                           ↓
                                          Agente de Menú Principal (si TRUE)
                                                           ↓
                                          Detectar Acción del Agente
                                                           ↓
                                          Router de Acciones
```

Pero después de ciertas acciones, se intenta volver a "Generar Menú Principal" directamente, lo cual puede causar inconsistencias.

**Nodos con Múltiples Salidas a "Generar Menú Principal":**
1. "Limpiar Output Después de Guardar"
2. "Router Preferencias" (outputs 1-5)
3. "Router Continuação" (output 3)

---

## 3. CONEXIONES DUPLICADAS O CONFLICTIVAS

### 🟡 ADVERTENCIA: "Crear Sesión de Compra" tiene 3 entradas

**Entradas desde:**
1. "Router de Acciones" (output 0) - ✅ CORRECTO
2. "Router de Opciones" (output 1) - ⚠️ DUPLICADO (nodo huérfano)
3. "¿Mostrar Menú o Chat?" (output 1) - ✅ CORRECTO
4. "Router Continuação" (output 0) - ⚠️ POSIBLE (pero nodo huérfano)

**Problema:**
Puede haber múltiples caminos que intenten crear sesiones duplicadas.

---

## 4. REFERENCIAS A NODOS EN CÓDIGO

### 🟢 VERIFICADAS: Referencias correctas encontradas

La mayoría de referencias en código JavaScript son correctas:
- `$('Extraer Datos WhatsApp').first().json`
- `$('Buscar Usuario').first().json`
- `$('Config Global').first().json`
- `$('Detectar Opción del Menú').first().json`

### 🔴 POSIBLES PROBLEMAS: Referencias que pueden fallar

En varios nodos se hace:
```javascript
const config = $('Config Global').first().json;
```

**Problema:**
Si "Config Global" no se ejecutó antes en el flujo, esta referencia fallará.

**Nodos Afectados:**
- "Calcular % Preferencias" (línea con PREFERENCE_FIELDS_TOTAL)
- "Generar Menú Principal" (líneas con WELCOME_MESSAGE, etc.)
- "Continuation Handler" (línea con CONTINUATION_MESSAGE)

---

## 5. PROBLEMAS ESPECÍFICOS DE LÓGICA

### 🔴 CRÍTICO: Detección de Duplicados de Fornecedor Incompleta

**Nodos Involucrados:**
- "Guardar Fornecedor BD"
- "Check If Duplicate"
- "Handle Duplicate Decision"
- "Detectar Decisión Duplicado"
- "Router: ¿Es Decisión Duplicado?"

**Problema:**
El flujo para manejar fornecedores duplicados está implementado pero:

1. "Guardar Fornecedor BD" ejecuta código que guarda DIRECTAMENTE sin verificar
2. "Check If Duplicate" se ejecuta DESPUÉS de guardar (debería ser ANTES)
3. El código de detección de duplicados busca en el output un marcador "DECISAO_DUPLICADO:" pero ningún agente lo genera

**Código Problemático en "Guardar Fornecedor BD":**
```javascript
// Buscar o crear proveedor
const { data: existingSupplier } = await $supabase
  .from('suppliers')
  .select('id')
  .ilike('company_name', datos.nome)
  .limit(1)
  .single();

if (existingSupplier) {
  // Actualizar
  supplierId = existingSupplier.id;
} else {
  // Crear nuevo
  supplierId = newSupplier.id;
}
```

**Resultado:**
Siempre actualiza si existe o crea si no existe. Nunca pregunta al usuario.

---

## 6. POSICIONAMIENTO DE NODOS

### Nodos Mal Posicionados

Varios nodos tienen posiciones que sugieren que fueron movidos pero no reconectados:

| Nodo | Posición | Problema |
|------|----------|----------|
| Config Global | [200, 200] | Está al inicio pero debería estar inline con el flujo |
| ¿Es Interacción de Menú? | [0, 1776] | Muy abajo, sugiere que fue movido |
| Detectar Opção Continuação | [2200, 2928] | Abajo derecha, desconectado del flujo |
| Global Error Handler | [2400, 3728] | Extremo inferior, nunca se alcanza |
| AI Error Handler | [2600, 3928] | Extremo inferior, nunca se alcanza |

---

## 7. RESUMEN DE IMPACTO

### 🔴 IMPACTO CRÍTICO - Workflow NO Funcional

**Funcionalidades Rotas:**
1. ❌ **Continuación después de acciones** - El usuario no puede elegir qué hacer después
2. ❌ **Manejo de errores** - Los errores no se capturan
3. ❌ **Menú de opciones** - El router está desconectado
4. ❌ **Detección de duplicados** - No pregunta al usuario

**Funcionalidades Que SÍ Funcionan:**
1. ✅ Onboarding de nuevos usuarios
2. ✅ Búsqueda de productos (vector search)
3. ✅ Agente de compras
4. ✅ Agente de subir precios (parcial)
5. ✅ Guardar preferencias

---

## 8. PRIORIDADES DE CORRECCIÓN

### 🔥 URGENTE (Impide Uso del Workflow)

1. **Conectar "Detectar Opção Continuação"** al flujo principal
2. **Conectar "Router de Opciones"** para que reciba datos
3. **Conectar "¿Es Interacción de Menú?"** al flujo principal

### ⚠️ IMPORTANTE (Mejora Estabilidad)

4. **Conectar Error Handlers** para capturar fallos
5. **Corregir lógica de duplicados** en registro de fornecedores
6. **Eliminar conexiones duplicadas** a "Crear Sesión de Compra"

### 💡 RECOMENDADO (Optimización)

7. Reorganizar posiciones de nodos para mejor visualización
8. Agregar nodos de validación entre secciones
9. Documentar flujos con Sticky Notes

---

## 9. PLAN DE ACCIÓN RECOMENDADO

### Paso 1: Corregir Flujo de Continuación
```
Enviar Respuesta → (Usuario responde vía WhatsApp Trigger)
                → Extraer Datos WhatsApp
                → Detectar si viene de continuación
                → Si TRUE: Detectar Opção Continuação
                → Router Continuação
```

### Paso 2: Conectar Router de Opciones
```
Detectar Opción del Menú → Router de Opciones
                         → Enrutar según opción detectada
```

### Paso 3: Implementar Manejo de Errores
```
(Cualquier nodo con error) → On Error → Global Error Handler
                                      → Enviar Respuesta con mensaje de error
```

### Paso 4: Corregir Detección de Duplicados
```
Agente Registrar Fornecedor → Detectar Fornecedor Completo
                            → Buscar Duplicados en DB
                            → Si hay duplicados: Preguntar al usuario
                            → Esperar decisión
                            → Handle Duplicate Decision
                            → Guardar según decisión
```

---

## 10. CÓDIGO DE AYUDA

### Script para Detectar Estado de Sesión

Agregar al inicio del flujo después de "Extraer Datos WhatsApp":

```javascript
// Detectar si el mensaje es parte de una sesión de continuación
const phoneNumber = $input.first().json.phone_number;

// Buscar sesión reciente completada esperando continuación
const { data: recentSession } = await $supabase
  .from('line_sessions')
  .select('*')
  .eq('channel_id', phoneNumber)
  .eq('awaiting_continuation', true)
  .order('session_end', { ascending: false })
  .limit(1)
  .single();

return [{
  json: {
    ...$input.first().json,
    is_continuation: !!recentSession,
    previous_session: recentSession
  }
}];
```

---

## CONCLUSIÓN

El workflow tiene una estructura sólida pero **múltiples conexiones críticas están rotas**.

**Estado Actual:** 🔴 NO FUNCIONAL para producción

**Estimación de Corrección:** 2-3 horas de trabajo

**Prioridad:** 🔥 URGENTE

---

*Generado automáticamente el 2025-11-10*
