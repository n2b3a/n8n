#!/usr/bin/env python3
"""
Corregir problemas REALES encontrados por el usuario
"""
import json
from pathlib import Path
from datetime import datetime

WORKFLOW_FILE = Path('workflow-frepi-mvp1-PRODUCTION-READY.json')
BACKUP_DIR = Path('backups')

# Create backup
BACKUP_DIR.mkdir(exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file = BACKUP_DIR / f'workflow_before_real_fixes_{timestamp}.json'

with open(WORKFLOW_FILE, 'r') as f:
    workflow = json.load(f)

with open(backup_file, 'w') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f"Backup: {backup_file}")
print("=" * 80)

# FIX 1: Cambiar Buscar Sesión Activa de Supabase a Code node
print("FIX 1: Buscar Sesión Activa - Cambiar de Supabase a Code")
print("=" * 80)

for node in workflow['nodes']:
    if node['name'] == 'Buscar Sesión Activa':
        print(f"Tipo anterior: {node['type']}")

        # Get current jsCode
        current_code = node['parameters'].get('jsCode', '')

        # Change type to Code
        node['type'] = 'n8n-nodes-base.code'
        node['typeVersion'] = 2

        # Update parameters
        node['parameters'] = {
            'mode': 'runOnceForAllItems',
            'jsCode': current_code
        }

        # Remove Supabase credential if exists
        if 'credentials' in node:
            del node['credentials']

        print(f"Tipo nuevo: {node['type']}")
        print("✓ Convertido a Code node")
        break

# FIX 2: Cambiar 'products' a 'master_list'
print("\nFIX 2: Cambiar referencias 'products' → 'master_list'")
print("=" * 80)

fixes_count = 0
for node in workflow['nodes']:
    if node['type'] == 'n8n-nodes-base.code':
        if 'parameters' in node and 'jsCode' in node['parameters']:
            code = node['parameters']['jsCode']

            # Replace references
            new_code = code.replace(".from('products')", ".from('master_list')")
            new_code = new_code.replace('.from("products")', '.from("master_list")')

            if new_code != code:
                node['parameters']['jsCode'] = new_code
                fixes_count += 1
                print(f"✓ Corregido: {node['name']}")

print(f"\nTotal nodos corregidos: {fixes_count}")

# Save
with open(WORKFLOW_FILE, 'w') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 80)
print("✅ CORRECCIONES COMPLETADAS")
print("=" * 80)
print(f"Workflow guardado: {WORKFLOW_FILE}")
