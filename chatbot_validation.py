#!/usr/bin/env python3
"""
CHATBOT-AWARE VALIDATION
Validates n8n chatbot workflows, understanding conversational patterns
"""

import json
import sys
from collections import defaultdict, deque

def load_workflow():
    with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def build_graph(workflow):
    """Build directed graph of connections"""
    nodes = workflow['nodes']
    connections = workflow['connections']

    node_names = {node['name'] for node in nodes}

    # Build adjacency list
    graph = defaultdict(list)
    reverse_graph = defaultdict(list)

    for source_name, conn_data in connections.items():
        if 'main' in conn_data:
            for output_list in conn_data['main']:
                for conn in output_list:
                    target_name = conn['node']
                    graph[source_name].append(target_name)
                    reverse_graph[target_name].append(source_name)

    return graph, reverse_graph, node_names

def check_critical_issues(workflow, graph):
    """Check for REAL problems that would break the workflow"""
    issues = []

    nodes = workflow['nodes']
    connections = workflow['connections']
    node_names = {node['name'] for node in nodes}

    # 1. Check for self-loops (node connecting to itself)
    for source_name, targets in graph.items():
        if source_name in targets:
            issues.append({
                'severity': 'CRITICAL',
                'type': 'Self-loop',
                'node': source_name,
                'description': f"Node '{source_name}' connects to itself - this will cause infinite recursion"
            })

    # 2. Check for missing target nodes
    for source_name, conn_data in connections.items():
        if 'main' in conn_data:
            for output_list in conn_data['main']:
                for conn in output_list:
                    target_name = conn['node']
                    if target_name not in node_names:
                        issues.append({
                            'severity': 'CRITICAL',
                            'type': 'Missing node',
                            'node': source_name,
                            'description': f"Connects to non-existent node '{target_name}'"
                        })

    # 3. Check for Code nodes without error handling
    for node in nodes:
        if node['type'] == 'n8n-nodes-base.code':
            code = node.get('parameters', {}).get('jsCode', '')
            if 'try' not in code or 'catch' not in code:
                issues.append({
                    'severity': 'WARNING',
                    'type': 'No error handling',
                    'node': node['name'],
                    'description': 'Code node without try-catch block'
                })

    # 4. Check for Switch nodes with obsolete format
    for node in nodes:
        if node['type'] == 'n8n-nodes-base.switch':
            output_expr = node.get('parameters', {}).get('output', '')
            if 'Output (' in output_expr:
                issues.append({
                    'severity': 'CRITICAL',
                    'type': 'Obsolete Switch format',
                    'node': node['name'],
                    'description': 'Using old Switch format - will fail in n8n 1.114.3+'
                })

    return issues

def check_chatbot_patterns(workflow, graph):
    """Verify chatbot-specific patterns are correct"""
    checks = []

    nodes = workflow['nodes']
    node_names = {node['name'] for node in nodes}

    # 1. Check trigger exists
    trigger_nodes = [n for n in nodes if 'trigger' in n['type'].lower() or 'whatsapp' in n['type'].lower()]
    if trigger_nodes:
        checks.append({
            'check': 'WhatsApp Trigger',
            'status': 'PASS',
            'details': f"Found: {', '.join([n['name'] for n in trigger_nodes])}"
        })
    else:
        checks.append({
            'check': 'WhatsApp Trigger',
            'status': 'FAIL',
            'details': 'No trigger node found'
        })

    # 2. Check output node exists (Enviar Respuesta)
    output_nodes = [n for n in nodes if 'enviar' in n['name'].lower() or 'send' in n['name'].lower()]
    if output_nodes:
        checks.append({
            'check': 'Response Node',
            'status': 'PASS',
            'details': f"Found: {', '.join([n['name'] for n in output_nodes])}"
        })
    else:
        checks.append({
            'check': 'Response Node',
            'status': 'FAIL',
            'details': 'No response/send node found'
        })

    # 3. Check Config Global exists
    if 'Config Global' in node_names:
        checks.append({
            'check': 'Config Global',
            'status': 'PASS',
            'details': 'Centralized config node exists'
        })
    else:
        checks.append({
            'check': 'Config Global',
            'status': 'WARNING',
            'details': 'No centralized config found'
        })

    # 4. Check error handlers exist
    error_handlers = [n for n in nodes if 'error' in n['name'].lower() and 'handler' in n['name'].lower()]
    if error_handlers:
        checks.append({
            'check': 'Error Handlers',
            'status': 'PASS',
            'details': f"Found: {', '.join([n['name'] for n in error_handlers])}"
        })
    else:
        checks.append({
            'check': 'Error Handlers',
            'status': 'WARNING',
            'details': 'No error handlers found'
        })

    # 5. Check AI retry logic (look for retry config in agent nodes)
    agent_nodes = [n for n in nodes if 'agent' in n['type'].lower()]
    agents_with_retry = 0
    for node in agent_nodes:
        options = node.get('parameters', {}).get('options', {})
        if options and isinstance(options, dict):
            if 'maxIterations' in str(options):
                agents_with_retry += 1

    if agent_nodes:
        if agents_with_retry == len(agent_nodes):
            checks.append({
                'check': 'AI Retry Logic',
                'status': 'PASS',
                'details': f'All {len(agent_nodes)} agent nodes have retry config'
            })
        else:
            checks.append({
                'check': 'AI Retry Logic',
                'status': 'WARNING',
                'details': f'{agents_with_retry}/{len(agent_nodes)} agents have retry config'
            })

    # 6. Check continuation flow exists
    continuation_nodes = [n for n in nodes if 'continuation' in n['name'].lower() or 'continuação' in n['name'].lower()]
    if continuation_nodes:
        checks.append({
            'check': 'Continuation Flow',
            'status': 'PASS',
            'details': f"Found: {', '.join([n['name'] for n in continuation_nodes])}"
        })
    else:
        checks.append({
            'check': 'Continuation Flow',
            'status': 'WARNING',
            'details': 'No continuation nodes found'
        })

    return checks

def main():
    print("=" * 80)
    print("CHATBOT-AWARE WORKFLOW VALIDATION")
    print("=" * 80)

    workflow = load_workflow()
    graph, reverse_graph, node_names = build_graph(workflow)

    print(f"\n📊 Workflow: {workflow.get('name', 'Unnamed')}")
    print(f"   Nodes: {len(node_names)}")
    print(f"   Connections: {sum(len(v) for v in graph.values())}")

    # Check for CRITICAL issues
    print("\n" + "=" * 80)
    print("CRITICAL ISSUES CHECK")
    print("=" * 80)

    issues = check_critical_issues(workflow, graph)
    critical_issues = [i for i in issues if i['severity'] == 'CRITICAL']
    warnings = [i for i in issues if i['severity'] == 'WARNING']

    if critical_issues:
        print(f"\n❌ Found {len(critical_issues)} CRITICAL issue(s):\n")
        for issue in critical_issues:
            print(f"   🚨 {issue['type']}: {issue['node']}")
            print(f"      {issue['description']}\n")
        print("⚠️  WORKFLOW WILL FAIL - Fix critical issues before importing!")
    else:
        print("\n✅ No critical issues found!")

    if warnings:
        print(f"\n⚠️  Found {len(warnings)} warning(s):")
        for warning in warnings:
            print(f"   - {warning['node']}: {warning['description']}")

    # Check chatbot patterns
    print("\n" + "=" * 80)
    print("CHATBOT PATTERN VALIDATION")
    print("=" * 80)

    checks = check_chatbot_patterns(workflow, graph)

    passed = sum(1 for c in checks if c['status'] == 'PASS')
    failed = sum(1 for c in checks if c['status'] == 'FAIL')
    warned = sum(1 for c in checks if c['status'] == 'WARNING')

    print()
    for check in checks:
        status_icon = '✅' if check['status'] == 'PASS' else '❌' if check['status'] == 'FAIL' else '⚠️'
        print(f"{status_icon} {check['check']}")
        print(f"   {check['details']}")

    # Final verdict
    print("\n" + "=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)

    if critical_issues:
        print(f"\n❌ WORKFLOW NOT READY")
        print(f"   Critical issues: {len(critical_issues)}")
        print(f"   Warnings: {len(warnings)}")
        print("\n🔧 Fix critical issues before importing to n8n")
        return 1
    elif failed > 0:
        print(f"\n⚠️  WORKFLOW HAS ISSUES")
        print(f"   Failed checks: {failed}")
        print(f"   Warnings: {warned}")
        print("\n🔧 Review failed checks before importing")
        return 1
    else:
        print(f"\n✅ WORKFLOW READY FOR PRODUCTION!")
        print(f"   Passed checks: {passed}")
        print(f"   Warnings: {warned}")
        print()
        print("🎉 You can safely import this workflow to n8n 1.114.3+")
        print()
        print("📋 Quick checklist before activating:")
        print("   1. Configure Supabase credentials")
        print("   2. Add OpenAI API key")
        print("   3. Setup WhatsApp Business API")
        print("   4. Test onboarding flow")
        print("   5. Test continuation flows")
        print("   6. Monitor logs for first interactions")
        return 0

if __name__ == '__main__':
    sys.exit(main())
