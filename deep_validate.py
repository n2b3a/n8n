#!/usr/bin/env python3
"""
Deep validation of n8n workflow to find "Could not find property option" error
"""

import json
import sys

def check_node_parameters(node):
    """Check for invalid parameters that n8n won't recognize"""
    issues = []
    node_name = node.get('name', 'Unknown')
    node_type = node.get('type', 'Unknown')
    params = node.get('parameters', {})

    # Check for common issues

    # 1. Code nodes should have proper structure
    if node_type == 'n8n-nodes-base.code':
        # Check language parameter
        if 'language' in params:
            lang = params['language']
            if lang not in ['javaScript', 'python']:
                issues.append(f"Invalid language: {lang}")

        # Should have jsCode if JavaScript
        if params.get('language') == 'javaScript':
            if 'jsCode' not in params:
                issues.append("Missing jsCode parameter for JavaScript code node")

    # 2. Switch nodes
    if node_type == 'n8n-nodes-base.switch':
        if 'rules' in params:
            rules = params['rules']
            if not isinstance(rules, dict):
                issues.append("Switch rules should be a dict")
            elif 'rules' not in rules:
                issues.append("Switch missing rules.rules structure")

    # 3. IF nodes
    if node_type == 'n8n-nodes-base.if':
        if 'conditions' in params:
            conditions = params['conditions']
            if not isinstance(conditions, dict):
                issues.append("IF conditions should be a dict")

    # 4. LangChain agent nodes
    if 'langchain.agent' in node_type:
        # Check for options vs direct parameters
        if 'options' in params:
            options = params['options']
            if 'systemMessage' in options:
                # This might be the issue - systemMessage in options
                pass

    # 5. Check for unknown/invalid parameters
    # Print all parameters for inspection
    if params:
        param_keys = list(params.keys())
        # Common valid keys
        valid_common = ['jsCode', 'language', 'mode', 'options', 'rules', 'conditions',
                       'resource', 'operation', 'text', 'promptType']

        for key in param_keys:
            if key not in valid_common and not key.startswith('_'):
                # Might be a custom parameter for this node type
                pass

    return issues

def inspect_all_nodes(workflow):
    """Inspect all nodes in detail"""
    print("=" * 80)
    print("DETAILED NODE INSPECTION")
    print("=" * 80)

    for idx, node in enumerate(workflow['nodes'], 1):
        node_name = node.get('name', 'Unknown')
        node_type = node.get('type', 'Unknown')
        node_id = node.get('id', 'Unknown')

        print(f"\n[{idx}] {node_name}")
        print(f"    Type: {node_type}")
        print(f"    ID: {node_id}")
        print(f"    TypeVersion: {node.get('typeVersion', 'N/A')}")

        # Check parameters
        params = node.get('parameters', {})
        if params:
            print(f"    Parameters ({len(params)} keys):")
            for key, value in params.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"      - {key}: <string, {len(value)} chars>")
                elif isinstance(value, dict):
                    print(f"      - {key}: <dict, {len(value)} keys>")
                    if key == 'options' and 'systemMessage' in value:
                        print(f"        → systemMessage: <{len(value['systemMessage'])} chars>")
                elif isinstance(value, list):
                    print(f"      - {key}: <list, {len(value)} items>")
                else:
                    print(f"      - {key}: {value}")

        # Check for issues
        issues = check_node_parameters(node)
        if issues:
            print(f"    ⚠️  ISSUES:")
            for issue in issues:
                print(f"      - {issue}")

def find_agent_nodes_with_options(workflow):
    """Find all agent nodes and check their structure"""
    print("\n" + "=" * 80)
    print("LANGCHAIN AGENT NODES ANALYSIS")
    print("=" * 80)

    for node in workflow['nodes']:
        if 'langchain' in node.get('type', '').lower():
            print(f"\nNode: {node['name']}")
            print(f"Type: {node['type']}")
            print(f"Parameters keys: {list(node.get('parameters', {}).keys())}")

            params = node.get('parameters', {})
            if 'options' in params:
                print(f"  → Has 'options' with keys: {list(params['options'].keys())}")

def main():
    print("🔍 Deep validation of n8n workflow...\n")

    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

    # Inspect all nodes
    inspect_all_nodes(workflow)

    # Special check for agent nodes
    find_agent_nodes_with_options(workflow)

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total nodes: {len(workflow['nodes'])}")
    print(f"Total connections: {len(workflow.get('connections', {}))}")

if __name__ == '__main__':
    main()
