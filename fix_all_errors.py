#!/usr/bin/env python3
"""
FIX ALL ERRORS - Reparación Completa del Workflow
==================================================

Corrige TODOS los errores reportados:
1. Nodos duplicados con mismo ID
2. Referencias a nodos inexistentes
3. Modelo OpenAI incorrecto
4. Configuración incorrecta de Switch
5. Parámetros incorrectos en Supabase
6. Verificación de conexiones

Fecha: 2025-11-10
Versión: 2.5.1 - Error Fixes
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import Counter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# File paths
WORKFLOW_FILE = Path(__file__).parent / 'workflow-frepi-mvp1-PRODUCTION-READY.json'
BACKUP_DIR = Path(__file__).parent / 'backups'
REPORT_FILE = Path(__file__).parent / 'ERROR_ANALYSIS_REPORT.md'


def create_backup(workflow_data: Dict) -> Path:
    """Create backup of current workflow"""
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BACKUP_DIR / f'workflow_before_fixes_{timestamp}.json'

    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(workflow_data, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Backup creado: {backup_file}")
    return backup_file


def find_node_by_name(workflow: Dict, name: str) -> Dict:
    """Find node by exact name"""
    for node in workflow['nodes']:
        if node['name'] == name:
            return node
    raise ValueError(f"Node '{name}' not found")


def find_all_node_names(workflow: Dict) -> Set[str]:
    """Get set of all node names"""
    return {node['name'] for node in workflow['nodes']}


# ============================================================================
# ERROR 1: ELIMINAR NODOS DUPLICADOS
# ============================================================================

def fix_1_remove_duplicate_nodes(workflow: Dict) -> Dict:
    """
    Eliminar nodos duplicados con mismo ID.

    PROBLEMA:
    - ¿Requiere Aclaración? aparece 2 veces (ID: clarification_if_node_id)
    - Generar Mensaje Aclaración aparece 2 veces (ID: clarification_message_node_id)

    SOLUCIÓN:
    - Mantener SOLO la primera ocurrencia
    - Eliminar duplicados
    """
    logger.info("=" * 80)
    logger.info("FIX 1: Eliminar Nodos Duplicados")
    logger.info("=" * 80)

    changes = []

    # Check for duplicate IDs
    ids_count = Counter([node.get('id') for node in workflow['nodes']])
    duplicates = {id_: count for id_, count in ids_count.items() if count > 1}

    if duplicates:
        logger.warning(f"⚠️ Encontrados {len(duplicates)} IDs duplicados:")
        for id_, count in duplicates.items():
            logger.warning(f"   - ID {id_}: {count} ocurrencias")

    # Track which nodes to keep (first occurrence only)
    seen_ids = {}
    nodes_to_remove = []

    for idx, node in enumerate(workflow['nodes']):
        node_id = node.get('id')
        node_name = node.get('name')

        if node_id in seen_ids:
            logger.warning(f"❌ Duplicado encontrado: '{node_name}' (ID: {node_id})")
            nodes_to_remove.append(idx)
            changes.append(f"Eliminado nodo duplicado: {node_name} (índice {idx})")
        else:
            seen_ids[node_id] = idx

    # Remove duplicates (in reverse to maintain indices)
    for idx in reversed(nodes_to_remove):
        removed_node = workflow['nodes'].pop(idx)
        logger.info(f"✓ Eliminado: {removed_node['name']} (ID: {removed_node['id']})")

    if not nodes_to_remove:
        logger.info("✓ No se encontraron nodos duplicados")

    return {
        'fix': 1,
        'name': 'Remove Duplicate Nodes',
        'changes': changes,
        'duplicates_removed': len(nodes_to_remove)
    }


# ============================================================================
# ERROR 2: CORREGIR REFERENCIAS A NODOS INEXISTENTES
# ============================================================================

def fix_2_correct_node_references(workflow: Dict) -> Dict:
    """
    Corregir referencias a 'Detectar Opción del Menú' que no existe.

    PROBLEMA:
    - Varios nodos referencian $('Detectar Opción del Menú') que NO existe

    SOLUCIÓN:
    - Cambiar a 'Detectar Acción del Agente' (que sí existe)
    """
    logger.info("=" * 80)
    logger.info("FIX 2: Corregir Referencias a Nodos Inexistentes")
    logger.info("=" * 80)

    changes = []

    # Get all valid node names
    valid_names = find_all_node_names(workflow)

    # Check if problematic reference exists
    if 'Detectar Opción del Menú' in valid_names:
        logger.info("✓ 'Detectar Opción del Menú' existe, no hay problema")
        return {'fix': 2, 'name': 'Correct Node References', 'changes': [], 'references_fixed': 0}

    # Find correct node name
    correct_name = 'Detectar Acción del Agente'
    if correct_name not in valid_names:
        logger.error(f"❌ Nodo correcto '{correct_name}' tampoco existe!")
        # Try to find similar
        similar = [n for n in valid_names if 'Detectar' in n and 'Acción' in n or 'Acci' in n]
        if similar:
            correct_name = similar[0]
            logger.info(f"✓ Usando nodo similar: '{correct_name}'")

    # Search and replace in all code nodes
    wrong_ref = "Detectar Opción del Menú"
    nodes_fixed = 0

    for node in workflow['nodes']:
        node_changed = False

        # Check jsCode
        if 'parameters' in node and 'jsCode' in node['parameters']:
            code = node['parameters']['jsCode']
            if wrong_ref in code:
                node['parameters']['jsCode'] = code.replace(
                    f"$('{wrong_ref}')",
                    f"$('{correct_name}')"
                )
                node_changed = True

        # Check fieldsUi (for Supabase nodes)
        if 'parameters' in node and 'fieldsUi' in node['parameters']:
            fields_ui = node['parameters']['fieldsUi']
            fields_str = json.dumps(fields_ui)
            if wrong_ref in fields_str:
                fields_str = fields_str.replace(
                    f"$('{wrong_ref}')",
                    f"$('{correct_name}')"
                )
                node['parameters']['fieldsUi'] = json.loads(fields_str)
                node_changed = True

        if node_changed:
            nodes_fixed += 1
            logger.info(f"✓ Corregido: {node['name']}")
            changes.append(f"Corregidas referencias en: {node['name']}")

    logger.info(f"✓ Total nodos corregidos: {nodes_fixed}")

    return {
        'fix': 2,
        'name': 'Correct Node References',
        'changes': changes,
        'references_fixed': nodes_fixed
    }


# ============================================================================
# ERROR 3: CORREGIR MODELO OPENAI
# ============================================================================

def fix_3_correct_openai_model(workflow: Dict) -> Dict:
    """
    Corregir modelo OpenAI de 'gpt-4.1-mini' a 'gpt-4o-mini'.

    PROBLEMA:
    - Varios nodos usan 'gpt-4.1-mini' que NO existe

    SOLUCIÓN:
    - Cambiar a 'gpt-4o-mini' (modelo real)
    """
    logger.info("=" * 80)
    logger.info("FIX 3: Corregir Modelo OpenAI")
    logger.info("=" * 80)

    changes = []
    wrong_model = "gpt-4.1-mini"
    correct_model = "gpt-4o-mini"
    nodes_fixed = 0

    for node in workflow['nodes']:
        if node['type'] == '@n8n/n8n-nodes-langchain.lmChatOpenAi':
            # Check if using wrong model
            if 'parameters' in node and 'model' in node['parameters']:
                model_config = node['parameters']['model']

                # Handle different model config formats
                if isinstance(model_config, dict):
                    if model_config.get('value') == wrong_model:
                        model_config['value'] = correct_model
                        nodes_fixed += 1
                        logger.info(f"✓ Corregido modelo en: {node['name']}")
                        changes.append(f"Modelo corregido en: {node['name']}")
                elif isinstance(model_config, str) and model_config == wrong_model:
                    node['parameters']['model'] = correct_model
                    nodes_fixed += 1
                    logger.info(f"✓ Corregido modelo en: {node['name']}")
                    changes.append(f"Modelo corregido en: {node['name']}")

    if nodes_fixed == 0:
        logger.info("✓ No se encontraron modelos incorrectos")
    else:
        logger.info(f"✓ Total nodos corregidos: {nodes_fixed}")

    return {
        'fix': 3,
        'name': 'Correct OpenAI Model',
        'changes': changes,
        'models_fixed': nodes_fixed
    }


# ============================================================================
# ERROR 4: CORREGIR CONFIGURACIÓN DE SWITCH
# ============================================================================

def fix_4_correct_switch_config(workflow: Dict) -> Dict:
    """
    Corregir configuración de Router Continuação.

    PROBLEMA:
    - Tiene campo 'output' en modo 'expression' (incompatible)

    SOLUCIÓN:
    - Eliminar campo 'output', dejar solo 'expression'
    """
    logger.info("=" * 80)
    logger.info("FIX 4: Corregir Configuración de Switch")
    logger.info("=" * 80)

    changes = []

    try:
        node = find_node_by_name(workflow, "Router Continuação")

        if 'parameters' in node:
            params = node['parameters']

            # Check if has both output and expression
            has_output = 'output' in params
            has_expression = 'expression' in params
            mode = params.get('mode')

            if mode == 'expression' and has_output:
                logger.warning(f"⚠️ Router Continuação tiene 'output' en modo 'expression'")
                del params['output']
                logger.info("✓ Eliminado campo 'output' conflictivo")
                changes.append("Eliminado campo 'output' de Router Continuação")
            else:
                logger.info("✓ Router Continuação configurado correctamente")

    except ValueError as e:
        logger.error(f"❌ Error: {e}")

    return {
        'fix': 4,
        'name': 'Correct Switch Config',
        'changes': changes
    }


# ============================================================================
# ERROR 5: CORREGIR SUPABASE FILTER
# ============================================================================

def fix_5_correct_supabase_filter(workflow: Dict) -> Dict:
    """
    Corregir filterBy en Update Session DB.

    PROBLEMA:
    - Usa filterBy con expresión (incorrecto)

    SOLUCIÓN:
    - Cambiar a filters con conditions
    """
    logger.info("=" * 80)
    logger.info("FIX 5: Corregir Supabase Filter")
    logger.info("=" * 80)

    changes = []

    try:
        node = find_node_by_name(workflow, "Update Session DB")

        if 'parameters' in node:
            params = node['parameters']

            # Check if using filterBy incorrectly
            if 'filterBy' in params and params.get('filterType') == 'manual':
                old_filter = params['filterBy']
                logger.warning(f"⚠️ Update Session DB usa filterBy con expresión")

                # Remove old filterBy
                del params['filterBy']

                # Add correct filters
                params['filters'] = {
                    'conditions': [{
                        'keyName': 'session_id',
                        'condition': 'eq',
                        'keyValue': '={{ $json._session_update.session_id }}'
                    }]
                }

                logger.info("✓ Convertido filterBy a filters con conditions")
                changes.append("Corregido filterBy en Update Session DB")
            else:
                logger.info("✓ Update Session DB configurado correctamente")

    except ValueError as e:
        logger.warning(f"⚠️ Nodo 'Update Session DB' no encontrado, puede no existir")

    return {
        'fix': 5,
        'name': 'Correct Supabase Filter',
        'changes': changes
    }


# ============================================================================
# VERIFICACIÓN COMPLETA
# ============================================================================

def verify_all_connections(workflow: Dict) -> Dict:
    """Verificar TODAS las conexiones y nodos huérfanos"""
    logger.info("=" * 80)
    logger.info("VERIFICACIÓN: Conexiones y Nodos Huérfanos")
    logger.info("=" * 80)

    connections = workflow.get('connections', {})
    all_nodes = {node['name'] for node in workflow['nodes']}

    # Nodes with incoming connections
    nodes_with_incoming = set()
    for source_node, conn_data in connections.items():
        if 'main' in conn_data:
            for outputs in conn_data['main']:
                if outputs:
                    for conn in outputs:
                        target = conn.get('node')
                        if target:
                            nodes_with_incoming.add(target)

    # Trigger nodes don't need incoming connections
    trigger_nodes = set()
    for node in workflow['nodes']:
        node_type = node.get('type', '').lower()
        if 'webhook' in node_type or 'trigger' in node_type:
            trigger_nodes.add(node['name'])

    # Sub-nodes (OpenAI models, memories) also don't need incoming
    sub_nodes = set()
    for node in workflow['nodes']:
        node_type = node.get('type', '')
        if any(x in node_type for x in ['lmChat', 'memory', 'embeddings', 'vectorStore']):
            sub_nodes.add(node['name'])

    # Find orphans
    orphans = []
    for node_name in all_nodes:
        if (node_name not in nodes_with_incoming and
            node_name not in trigger_nodes and
            node_name not in sub_nodes):
            orphans.append(node_name)

    # Check for broken connections
    broken_connections = []
    for source_node, conn_data in connections.items():
        if source_node not in all_nodes:
            broken_connections.append(f"Conexión desde nodo inexistente: {source_node}")

        if 'main' in conn_data:
            for output_idx, outputs in enumerate(conn_data['main']):
                if outputs:
                    for conn in outputs:
                        target = conn.get('node')
                        if target and target not in all_nodes:
                            broken_connections.append(
                                f"{source_node} → {target} (nodo destino no existe)"
                            )

    # Report
    if orphans:
        logger.warning(f"⚠️ {len(orphans)} nodos huérfanos (sin conexiones entrantes):")
        for orphan in orphans:
            logger.warning(f"   - {orphan}")
    else:
        logger.info("✅ No hay nodos huérfanos")

    if broken_connections:
        logger.error(f"❌ {len(broken_connections)} conexiones rotas:")
        for broken in broken_connections:
            logger.error(f"   - {broken}")
    else:
        logger.info("✅ No hay conexiones rotas")

    return {
        'total_nodes': len(all_nodes),
        'trigger_nodes': len(trigger_nodes),
        'sub_nodes': len(sub_nodes),
        'orphan_nodes': orphans,
        'broken_connections': broken_connections,
        'status': 'OK' if not broken_connections else 'ERROR'
    }


def generate_error_report(fixes: List[Dict], verification: Dict):
    """Generate comprehensive error report"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    report = f"""# ERROR ANALYSIS REPORT

**Fecha:** {timestamp}
**Workflow:** workflow-frepi-mvp1-PRODUCTION-READY.json

## RESUMEN DE CORRECCIONES

"""

    total_changes = sum(len(fix['changes']) for fix in fixes)
    report += f"Total de correcciones aplicadas: **{total_changes}**\n\n"

    for fix in fixes:
        report += f"### {fix['name']}\n\n"
        if fix['changes']:
            for change in fix['changes']:
                report += f"- ✅ {change}\n"
        else:
            report += "- ℹ️ No se requirieron cambios\n"
        report += "\n"

    report += "## VERIFICACIÓN FINAL\n\n"
    report += f"- **Total nodos:** {verification['total_nodes']}\n"
    report += f"- **Nodos trigger:** {verification['trigger_nodes']}\n"
    report += f"- **Sub-nodos (AI):** {verification['sub_nodes']}\n"
    report += f"- **Nodos huérfanos:** {len(verification['orphan_nodes'])}\n"
    report += f"- **Conexiones rotas:** {len(verification['broken_connections'])}\n"
    report += f"- **Estado:** {'✅ OK' if verification['status'] == 'OK' else '❌ ERROR'}\n\n"

    if verification['orphan_nodes']:
        report += "### Nodos Huérfanos\n\n"
        for orphan in verification['orphan_nodes']:
            report += f"- ⚠️ {orphan}\n"
        report += "\n"

    if verification['broken_connections']:
        report += "### Conexiones Rotas\n\n"
        for broken in verification['broken_connections']:
            report += f"- ❌ {broken}\n"
        report += "\n"

    report += "---\n\n**Estado Final:** "
    if verification['status'] == 'OK' and len(verification['orphan_nodes']) == 0:
        report += "✅ WORKFLOW CORREGIDO Y VERIFICADO\n"
    elif verification['status'] == 'OK':
        report += "⚠️ WORKFLOW FUNCIONAL (con nodos huérfanos no críticos)\n"
    else:
        report += "❌ REQUIERE REVISIÓN MANUAL\n"

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)

    logger.info(f"✅ Reporte generado: {REPORT_FILE}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main fix function"""
    logger.info("=" * 80)
    logger.info("FIX ALL ERRORS - Reparación Completa")
    logger.info("=" * 80)
    logger.info(f"Workflow file: {WORKFLOW_FILE}")
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    # Load workflow
    logger.info("Loading workflow...")
    with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    logger.info(f"✓ Workflow loaded: {len(workflow['nodes'])} nodes")

    # Create backup
    backup_file = create_backup(workflow)

    # Apply all fixes
    fixes = []

    # FIX 1: Remove duplicate nodes
    result1 = fix_1_remove_duplicate_nodes(workflow)
    fixes.append(result1)

    # FIX 2: Correct node references
    result2 = fix_2_correct_node_references(workflow)
    fixes.append(result2)

    # FIX 3: Correct OpenAI model
    result3 = fix_3_correct_openai_model(workflow)
    fixes.append(result3)

    # FIX 4: Correct Switch config
    result4 = fix_4_correct_switch_config(workflow)
    fixes.append(result4)

    # FIX 5: Correct Supabase filter
    result5 = fix_5_correct_supabase_filter(workflow)
    fixes.append(result5)

    # Verify everything
    verification = verify_all_connections(workflow)

    # Save workflow
    logger.info("=" * 80)
    logger.info("Saving workflow...")
    with open(WORKFLOW_FILE, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Workflow saved: {WORKFLOW_FILE}")

    # Generate report
    generate_error_report(fixes, verification)

    # Final summary
    logger.info("=" * 80)
    logger.info("✅ REPARACIÓN COMPLETADA")
    logger.info("=" * 80)
    logger.info(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    total_changes = sum(len(fix['changes']) for fix in fixes)
    logger.info(f"Correcciones aplicadas: {total_changes}")
    logger.info(f"Nodos huérfanos: {len(verification['orphan_nodes'])}")
    logger.info(f"Conexiones rotas: {len(verification['broken_connections'])}")
    logger.info(f"Estado: {verification['status']}")
    logger.info("=" * 80)

    # Print summary
    print("\n" + "=" * 80)
    print("RESUMEN DE CORRECCIONES")
    print("=" * 80)

    for fix in fixes:
        status = "✅" if fix['changes'] else "ℹ️"
        print(f"{status} {fix['name']}: {len(fix['changes'])} cambios")

    print(f"\n{'✅' if verification['status'] == 'OK' else '❌'} Verificación: {verification['status']}")
    print(f"⚠️  Nodos huérfanos: {len(verification['orphan_nodes'])}")
    print(f"{'❌' if verification['broken_connections'] else '✅'} Conexiones rotas: {len(verification['broken_connections'])}")

    print("\n" + "=" * 80)
    print("ARCHIVOS CREADOS:")
    print("=" * 80)
    print(f"✓ {REPORT_FILE}")
    print(f"✓ {backup_file}")
    print("=" * 80)

    return 0 if verification['status'] == 'OK' else 1


if __name__ == '__main__':
    exit(main())
