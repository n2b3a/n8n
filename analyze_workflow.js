// Script para analizar el workflow y encontrar problemas
const workflow = require('./workflow-frepi-mvp1-mejorado.json');

console.log('🔍 ANALIZANDO WORKFLOW: ' + workflow.name);
console.log('━'.repeat(80));

const nodes = workflow.nodes;
const connections = workflow.connections;

// 1. Crear mapas de nodos por ID y nombre
const nodeById = {};
const nodeByName = {};
nodes.forEach(node => {
  nodeById[node.id] = node;
  nodeByName[node.name] = node;
});

console.log(`\n📊 Total de nodos: ${nodes.length}`);

// 2. Encontrar nodos sin conexiones de entrada (excepto triggers)
console.log('\n\n🔴 NODOS SIN CONEXIÓN DE ENTRADA (posibles huérfanos):');
console.log('━'.repeat(80));

const nodesWithInputs = new Set();

// Marcar nodos con conexiones
Object.keys(connections).forEach(sourceName => {
  const nodeConnections = connections[sourceName];
  if (nodeConnections.main) {
    nodeConnections.main.forEach(outputArray => {
      outputArray.forEach(connection => {
        nodesWithInputs.add(connection.node);
      });
    });
  }
});

let orphanCount = 0;
nodes.forEach(node => {
  const isOrphan = !nodesWithInputs.has(node.name) &&
                   !node.type.includes('Trigger') &&
                   node.name !== 'WhatsApp Trigger';

  if (isOrphan) {
    orphanCount++;
    console.log(`   ${orphanCount}. "${node.name}" (ID: ${node.id})`);
    console.log(`      Tipo: ${node.type}`);
    console.log(`      Posición: [${node.position}]`);
    console.log('');
  }
});

if (orphanCount === 0) {
  console.log('   ✅ No se encontraron nodos huérfanos');
}

// 3. Encontrar nodos sin conexiones de salida
console.log('\n\n🟡 NODOS SIN CONEXIÓN DE SALIDA:');
console.log('━'.repeat(80));

const nodesWithOutputs = new Set(Object.keys(connections));
let deadEndCount = 0;

nodes.forEach(node => {
  if (!nodesWithOutputs.has(node.name) &&
      !node.name.includes('Enviar') &&
      !node.name.includes('Guardar') &&
      !node.name.includes('Actualizar')) {
    deadEndCount++;
    console.log(`   ${deadEndCount}. "${node.name}" (ID: ${node.id})`);
    console.log(`      Tipo: ${node.type}`);
    console.log('');
  }
});

if (deadEndCount === 0) {
  console.log('   ✅ Todos los nodos tienen salidas (excepto finales)');
}

// 4. Analizar referencias a nodos en código JavaScript
console.log('\n\n🔍 REFERENCIAS A NODOS EN CÓDIGO:');
console.log('━'.repeat(80));

const codeNodes = nodes.filter(n => n.type === 'n8n-nodes-base.code');
let invalidReferences = 0;

codeNodes.forEach(node => {
  const code = node.parameters?.jsCode || '';

  // Buscar referencias $('NombreNodo')
  const regex = /\$\(['"]([^'"]+)['"]\)/g;
  let match;
  const references = [];

  while ((match = regex.exec(code)) !== null) {
    references.push(match[1]);
  }

  // Verificar si los nodos referenciados existen
  references.forEach(refName => {
    if (!nodeByName[refName]) {
      invalidReferences++;
      console.log(`   ❌ "${node.name}" referencia a "${refName}" que NO EXISTE`);
    }
  });
});

if (invalidReferences === 0) {
  console.log('   ✅ Todas las referencias son válidas');
} else {
  console.log(`\n   Total de referencias inválidas: ${invalidReferences}`);
}

// 5. Verificar flujo principal
console.log('\n\n🌊 ANÁLISIS DE FLUJO PRINCIPAL:');
console.log('━'.repeat(80));

console.log('\n   Punto de inicio: WhatsApp Trigger');
console.log('   → Config Global');
console.log('   → Extraer Datos WhatsApp');

// Verificar que el flujo principal esté bien conectado
const mainFlowNodes = [
  'WhatsApp Trigger',
  'Config Global',
  'Extraer Datos WhatsApp',
  '¿Archivo No Soportado?',
  'Buscar Usuario',
  '¿Usuario Existe?'
];

mainFlowNodes.forEach((nodeName, index) => {
  if (index === 0) return; // Skip trigger

  const hasConnection = nodesWithInputs.has(nodeName);
  const status = hasConnection ? '✅' : '❌';
  console.log(`   ${status} ${nodeName}`);
});

console.log('\n\n━'.repeat(80));
console.log('✅ ANÁLISIS COMPLETO');
console.log('━'.repeat(80));
