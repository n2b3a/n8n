#!/usr/bin/env python3
"""
COMPREHENSIVE WORKFLOW ANALYSIS

Check for ALL potential issues based on lessons learned:
1. Switch nodes missing outputsAmount
2. Code nodes with duplicate variable declarations
3. Nodes referencing data that might not exist
4. Config Global structure and references
5. Data flow issues
6. Connection issues
"""

import json
import sys
import re

def check_switch_nodes(workflow):
    """Check all Switch nodes have correct configuration"""
    print("\n" + "="*80)
    print("1. SWITCH NODE CONFIGURATION")
    print("="*80)

    nodes = workflow['nodes']
    connections = workflow['connections']
    switch_nodes = [n for n in nodes if n['type'] == 'n8n-nodes-base.switch']

    issues = []

    for node in switch_nodes:
        name = node['name']
        params = node.get('parameters', {})
        outputs_amount = params.get('options', {}).get('outputsAmount')

        # Count connections
        node_conns = connections.get(name, {}).get('main', [])
        actual_outputs = len(node_conns)

        if outputs_amount is None:
            issues.append(f"❌ {name}: Missing outputsAmount parameter")
        elif outputs_amount != actual_outputs:
            issues.append(f"⚠️ {name}: outputsAmount={outputs_amount} but {actual_outputs} connections")
        else:
            print(f"✅ {name}: {outputs_amount} outputs configured correctly")

    if issues:
        print("\n❌ Issues found:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print(f"\n✅ All {len(switch_nodes)} Switch nodes configured correctly")
        return True

def check_code_node_variables(workflow):
    """Check Code nodes for duplicate variable declarations"""
    print("\n" + "="*80)
    print("2. CODE NODE VARIABLE DECLARATIONS")
    print("="*80)

    nodes = workflow['nodes']
    code_nodes = [n for n in nodes if n['type'] == 'n8n-nodes-base.code']

    issues = []

    for node in code_nodes:
        name = node['name']
        code = node.get('parameters', {}).get('jsCode', '')

        # Check for duplicate const declarations
        const_declarations = re.findall(r'const\s+(\w+)\s*=', code)

        duplicates = []
        seen = set()
        for var in const_declarations:
            if var in seen:
                duplicates.append(var)
            seen.add(var)

        if duplicates:
            issues.append(f"❌ {name}: Duplicate const declarations: {', '.join(set(duplicates))}")

    if issues:
        print("\n❌ Issues found:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print(f"\n✅ All {len(code_nodes)} Code nodes have no duplicate declarations")
        return True

def check_config_global(workflow):
    """Check Config Global configuration"""
    print("\n" + "="*80)
    print("3. CONFIG GLOBAL CONFIGURATION")
    print("="*80)

    nodes = workflow['nodes']
    connections = workflow['connections']

    # Find Config Global
    config_node = None
    for node in nodes:
        if node['name'] == 'Config Global':
            config_node = node
            break

    if not config_node:
        print("❌ Config Global node not found!")
        return False

    # Check it's a Code node
    if config_node['type'] != 'n8n-nodes-base.code':
        print(f"❌ Config Global is {config_node['type']}, should be n8n-nodes-base.code")
        return False
    else:
        print("✅ Config Global is Code node")

    # Check it preserves input
    code = config_node.get('parameters', {}).get('jsCode', '')
    if '...input' not in code:
        print("❌ Config Global doesn't preserve input data (...input)")
        return False
    else:
        print("✅ Config Global preserves input data")

    # Check it returns flat structure
    if '...config' not in code:
        print("⚠️  Config Global might not return flat structure (...config)")
    else:
        print("✅ Config Global returns flat structure")

    # Check it's connected in the flow
    if 'Config Global' not in connections:
        print("❌ Config Global has no outgoing connections!")
        return False
    else:
        print("✅ Config Global is connected to flow")

    return True

def check_config_references(workflow):
    """Check nodes that reference Config Global"""
    print("\n" + "="*80)
    print("4. CONFIG GLOBAL REFERENCES")
    print("="*80)

    nodes = workflow['nodes']
    issues = []

    reference_patterns = [
        (r"\$json\.config\.", "Uses $json.config (may fail if not in flow path)"),
        (r"\$\('Config Global'\)\.first\(\)\.json\.config\.", "References nested config (should be flat)"),
    ]

    for node in nodes:
        if node['type'] != 'n8n-nodes-base.code':
            continue

        name = node['name']
        code = node.get('parameters', {}).get('jsCode', '')

        for pattern, description in reference_patterns:
            if re.search(pattern, code):
                issues.append(f"⚠️ {name}: {description}")

    if issues:
        print("\n⚠️ Potential issues found:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✅ All Config Global references use correct format")
        return True

def check_data_flow(workflow):
    """Check critical data flow paths"""
    print("\n" + "="*80)
    print("5. CRITICAL DATA FLOW PATHS")
    print("="*80)

    nodes = workflow['nodes']
    connections = workflow['connections']

    # Check critical path: WhatsApp Trigger → Config Global → Extraer Datos
    checks = []

    # Find nodes
    trigger = next((n for n in nodes if 'trigger' in n['type'].lower()), None)
    config = next((n for n in nodes if n['name'] == 'Config Global'), None)
    extraer = next((n for n in nodes if n['name'] == 'Extraer Datos WhatsApp'), None)

    if not trigger:
        checks.append("❌ No WhatsApp Trigger found")
    else:
        trigger_name = trigger['name']
        trigger_conn = connections.get(trigger_name, {}).get('main', [[]])[0]
        if trigger_conn and trigger_conn[0]['node'] == 'Config Global':
            checks.append(f"✅ {trigger_name} → Config Global")
        else:
            target = trigger_conn[0]['node'] if trigger_conn else 'None'
            checks.append(f"❌ {trigger_name} → {target} (should be Config Global)")

    if config:
        config_conn = connections.get('Config Global', {}).get('main', [[]])[0]
        if config_conn and config_conn[0]['node'] == 'Extraer Datos WhatsApp':
            checks.append("✅ Config Global → Extraer Datos WhatsApp")
        else:
            target = config_conn[0]['node'] if config_conn else 'None'
            checks.append(f"❌ Config Global → {target} (should be Extraer Datos WhatsApp)")

    if extraer:
        code = extraer.get('parameters', {}).get('jsCode', '')
        if 'data.messages' in code or 'input.messages' in code:
            checks.append("✅ Extraer Datos expects messages field")
        else:
            checks.append("⚠️ Extraer Datos might not check for messages")

    for check in checks:
        print(f"   {check}")

    return all('✅' in check for check in checks)

def check_error_handling(workflow):
    """Check error handling in Code nodes"""
    print("\n" + "="*80)
    print("6. ERROR HANDLING IN CODE NODES")
    print("="*80)

    nodes = workflow['nodes']
    code_nodes = [n for n in nodes if n['type'] == 'n8n-nodes-base.code']

    with_error_handling = 0
    without_error_handling = []

    for node in code_nodes:
        name = node['name']
        code = node.get('parameters', {}).get('jsCode', '')

        if 'try' in code and 'catch' in code:
            with_error_handling += 1
        else:
            without_error_handling.append(name)

    print(f"\n📊 Code nodes with error handling: {with_error_handling}/{len(code_nodes)}")

    if without_error_handling:
        print(f"\n⚠️ Nodes without error handling:")
        for name in without_error_handling[:10]:  # Show max 10
            print(f"   - {name}")
        if len(without_error_handling) > 10:
            print(f"   ... and {len(without_error_handling) - 10} more")

    return True  # Not critical

def main():
    print("="*80)
    print("COMPREHENSIVE WORKFLOW ANALYSIS")
    print("="*80)
    print("\nAnalyzing workflow for ALL potential issues...")

    # Load workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"\n✅ Workflow loaded: {len(workflow['nodes'])} nodes")
    except Exception as e:
        print(f"\n❌ Error loading workflow: {e}")
        sys.exit(1)

    # Run all checks
    results = {}
    results['switch_nodes'] = check_switch_nodes(workflow)
    results['code_variables'] = check_code_node_variables(workflow)
    results['config_global'] = check_config_global(workflow)
    results['config_references'] = check_config_references(workflow)
    results['data_flow'] = check_data_flow(workflow)
    results['error_handling'] = check_error_handling(workflow)

    # Summary
    print("\n" + "="*80)
    print("ANALYSIS SUMMARY")
    print("="*80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nChecks passed: {passed}/{total}\n")

    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {check_name}")

    if all(results.values()):
        print("\n✅ ALL CHECKS PASSED!")
        print("   Workflow appears to be correctly configured")
        return 0
    else:
        print("\n⚠️ SOME CHECKS FAILED")
        print("   Review issues above before importing to n8n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
