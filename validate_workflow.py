#!/usr/bin/env python3
"""
Validate and fix n8n workflow JSON structure
"""

import json
import sys

def validate_node_structure(node):
    """Validate that a node has required fields"""
    issues = []

    # Check required fields
    required = ['id', 'name', 'type', 'position', 'parameters']
    for field in required:
        if field not in node:
            issues.append(f"Missing required field: {field}")

    # Check position format
    if 'position' in node:
        if not isinstance(node['position'], list) or len(node['position']) != 2:
            issues.append(f"Invalid position format: {node.get('position')}")

    # Check parameters
    if 'parameters' in node and node['type'] == 'n8n-nodes-base.code':
        params = node['parameters']

        # Code node should have jsCode
        if 'jsCode' not in params and 'language' in params:
            if params.get('language') == 'javaScript':
                issues.append("Code node missing jsCode parameter")

    # Check if node has typeVersion
    if 'typeVersion' not in node:
        issues.append("Missing typeVersion")

    return issues

def validate_connections(workflow):
    """Validate connections reference existing nodes"""
    issues = []
    node_ids = {node['id'] for node in workflow['nodes']}
    node_names = {node['name'] for node in workflow['nodes']}

    for source, connections in workflow.get('connections', {}).items():
        # Source should exist
        if source not in node_names:
            issues.append(f"Connection source '{source}' not found in nodes")
            continue

        # Check connection structure
        if isinstance(connections, dict):
            for conn_type, conn_list in connections.items():
                if not isinstance(conn_list, list):
                    issues.append(f"Invalid connection list for {source}.{conn_type}")
                    continue

                for conn_group in conn_list:
                    if not isinstance(conn_group, list):
                        issues.append(f"Invalid connection group in {source}.{conn_type}")
                        continue

                    for conn in conn_group:
                        if not isinstance(conn, dict):
                            issues.append(f"Invalid connection object in {source}")
                            continue

                        if 'node' not in conn:
                            issues.append(f"Connection missing 'node' field in {source}")
                            continue

                        target = conn['node']
                        if target not in node_names:
                            issues.append(f"Connection target '{target}' not found (from {source})")

    return issues

def find_problematic_nodes(workflow):
    """Find nodes that might cause import issues"""
    problems = []

    for node in workflow['nodes']:
        node_name = node.get('name', 'Unknown')
        node_type = node.get('type', 'Unknown')

        print(f"\n🔍 Checking node: {node_name} ({node_type})")

        # Validate structure
        node_issues = validate_node_structure(node)
        if node_issues:
            problems.append({
                'node': node_name,
                'id': node.get('id'),
                'issues': node_issues
            })
            print(f"  ❌ Issues found:")
            for issue in node_issues:
                print(f"     - {issue}")
        else:
            print(f"  ✅ Structure OK")

    return problems

def main():
    print("🔍 Validating n8n workflow structure...\n")

    # Load workflow
    try:
        with open('/home/user/n8n/workflow-frepi-mvp1-mejorado.json', 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"✅ Loaded workflow: {workflow.get('name', 'Unknown')}")
        print(f"   Nodes: {len(workflow.get('nodes', []))}")
        print(f"   Connections: {len(workflow.get('connections', {}))}")
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

    # Validate nodes
    print("\n" + "="*60)
    print("VALIDATING NODES")
    print("="*60)

    node_problems = find_problematic_nodes(workflow)

    # Validate connections
    print("\n" + "="*60)
    print("VALIDATING CONNECTIONS")
    print("="*60)

    conn_issues = validate_connections(workflow)
    if conn_issues:
        print("\n❌ Connection issues found:")
        for issue in conn_issues:
            print(f"  - {issue}")
    else:
        print("\n✅ All connections valid")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    total_issues = len(node_problems) + len(conn_issues)

    if total_issues == 0:
        print("✅ No issues found! Workflow should import correctly.")
    else:
        print(f"❌ Found {total_issues} issue(s):")
        print(f"   - Node issues: {len(node_problems)}")
        print(f"   - Connection issues: {len(conn_issues)}")

        if node_problems:
            print("\n🔧 Nodes with issues:")
            for prob in node_problems:
                print(f"   • {prob['node']} (ID: {prob['id']})")
                for issue in prob['issues']:
                    print(f"     - {issue}")

    return total_issues

if __name__ == '__main__':
    issues = main()
    sys.exit(0 if issues == 0 else 1)
