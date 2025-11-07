#!/usr/bin/env python3
"""
SPRINT 2 - FIX #4: Structured Logging
Add consistent logging format to all Code nodes
"""

import json
import sys
import re

def add_structured_logging(workflow):
    """Add structured logging helper to all Code nodes"""
    print("=" * 80)
    print("SPRINT 2 - FIX #4: STRUCTURED LOGGING")
    print("=" * 80)

    nodes = workflow['nodes']
    updated_count = 0

    for node in nodes:
        if node['type'] != 'n8n-nodes-base.code':
            continue

        code = node['parameters'].get('jsCode', '')
        node_name = node['name']

        # Skip if already has LOG object
        if 'const LOG = {' in code:
            print(f"  ℹ️  {node_name:45} - Already has structured logging")
            continue

        print(f"\n🔧 Adding structured logging: {node_name}")

        # Create LOG helper
        log_helper = f"""// ===== STRUCTURED LOGGING =====
const LOG = {{
  prefix: '[{node_name}]',
  info: (msg, data) => console.log(`${{LOG.prefix}} ℹ️  ${{msg}}`, data !== undefined ? JSON.stringify(data).substring(0, 200) : ''),
  success: (msg, data) => console.log(`${{LOG.prefix}} ✅ ${{msg}}`, data !== undefined ? JSON.stringify(data).substring(0, 200) : ''),
  error: (msg, err) => console.error(`${{LOG.prefix}} ❌ ${{msg}}`, err || ''),
  warn: (msg) => console.warn(`${{LOG.prefix}} ⚠️  ${{msg}}`)
}};
// ===== END LOGGING =====

"""

        # Replace old console.log patterns with LOG methods
        code_updated = code

        # Replace console.log with LOG.info
        code_updated = re.sub(
            r"console\.log\(`✅\s*\[([^\]]+)\]([^`]+)`([^)]*)\)",
            r"LOG.success('\2'.trim()\3)",
            code_updated
        )

        code_updated = re.sub(
            r"console\.log\(`([^`]*)`([^)]*)\)",
            r"LOG.info('\1'\2)",
            code_updated
        )

        # Replace console.error with LOG.error
        code_updated = re.sub(
            r"console\.error\(`❌\s*\[([^\]]+)\]([^`]+)`([^)]*)\)",
            r"LOG.error('\2'.trim()\3)",
            code_updated
        )

        code_updated = re.sub(
            r"console\.error\(`([^`]*)`([^)]*)\)",
            r"LOG.error('\1'\2)",
            code_updated
        )

        # Replace console.warn with LOG.warn
        code_updated = re.sub(
            r"console\.warn\(`([^`]*)`([^)]*)\)",
            r"LOG.warn('\1'\2)",
            code_updated
        )

        # Insert LOG helper after try { or at the beginning
        if '// ===== ERROR HANDLING & INPUT VALIDATION =====' in code_updated:
            # Insert after the try { line
            code_updated = code_updated.replace(
                '  // Original code starts here',
                log_helper + '  // Original code starts here'
            )
        else:
            # Insert at the beginning
            code_updated = log_helper + code_updated

        node['parameters']['jsCode'] = code_updated
        updated_count += 1
        print(f"  ✅ Structured logging added")

    return updated_count

def main():
    print("🚀 Starting Sprint 2 - Fix #4: Structured Logging\n")

    # Load workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Workflow loaded: {len(workflow['nodes'])} nodes\n")
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

    # Apply structured logging
    updated = add_structured_logging(workflow)

    # Save workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Workflow saved: {len(workflow['nodes'])} nodes")
    except Exception as e:
        print(f"\n❌ Error saving workflow: {e}")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("SPRINT 2 - FIX #4 COMPLETED")
    print("=" * 80)
    print(f"\nNodes with structured logging: {updated}")
    print("\nLogging format:")
    print("  LOG.info('message', data)    - Informational")
    print("  LOG.success('message', data) - Success with ✅")
    print("  LOG.error('message', error)  - Error with ❌")
    print("  LOG.warn('message')          - Warning with ⚠️")
    print("\n🎯 Logs are now consistent and easy to search!")

if __name__ == '__main__':
    main()
