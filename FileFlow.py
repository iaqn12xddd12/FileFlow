# =========================================================
# FileFlow - Python Import Visualizer
# Author: Ali Rajabpour Sanati
# Website: Rajabpour.com
# GitHub: https://github.com/ali-rajabpour
# =========================================================

import os
import ast
import argparse
from collections import defaultdict



def find_py_files(root_dir):
    py_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                full_path = os.path.abspath(os.path.join(dirpath, filename))
                py_files.append(full_path)
    print(f"[FileFlow] Found {len(py_files)} Python files in {root_dir}")
    return py_files


def module_name_from_path(py_file, root_dir):
    rel_path = os.path.relpath(py_file, root_dir)
    no_ext = os.path.splitext(rel_path)[0]
    return no_ext.replace(os.sep, '.')


def parse_imports(py_file, file_modname):
    imports = set()
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=py_file)
            except Exception as e:
                print(f"[FileFlow] Skipping {py_file}: {e}")
                return imports  # skip files with syntax errors
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        if node.level == 0:
                            imports.add(node.module)
                        else:
                            # Handle relative imports
                            parent_mod = file_modname.split('.')[:-node.level]
                            if parent_mod:
                                rel_mod = '.'.join(parent_mod + [node.module])
                                imports.add(rel_mod)
                            else:
                                imports.add(node.module)
                    elif node.level > 0:
                        # from . import foo
                        parent_mod = file_modname.split('.')[:-node.level]
                        if parent_mod:
                            imports.add('.'.join(parent_mod))
    except Exception as e:
        print(f"[FileFlow] Error reading {py_file}: {e}")
    return imports


def build_dependency_graph(py_files, root_dir):
    module_to_file = {module_name_from_path(f, root_dir): f for f in py_files}
    dependencies = defaultdict(set)
    for py_file in py_files:
        this_mod = module_name_from_path(py_file, root_dir)
        imports = parse_imports(py_file, this_mod)
        for imp in imports:
            # Exact match
            if imp in module_to_file:
                dependencies[this_mod].add(imp)
            else:
                # Try matching submodules and __init__
                for mod in module_to_file:
                    if mod.endswith('.' + imp) or mod == imp or (mod + '.__init__' == imp):
                        dependencies[this_mod].add(mod)
    # Ensure all modules (even those with no edges) are nodes
    for mod in module_to_file:
        if mod not in dependencies:
            dependencies[mod] = set()
    return dependencies, module_to_file




def write_markdown(dependencies, md_path):
    total_edges = sum(len(targets) for targets in dependencies.values())
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('graph TD\n')
        edge_count = 0
        nodes = set(dependencies.keys())
        def to_id(name):
            # Replace invalid chars for Mermaid IDs (no quotes, no dots)
            return name.replace('.', '_').replace('-', '_').replace('/', '_').replace('__', '_').replace(' ', '_')

        written_nodes = set()
        for src, targets in sorted(dependencies.items()):
            src_id = to_id(src)
            if targets:
                for tgt in sorted(targets):
                    tgt_id = to_id(tgt)
                    # Write edge with labels
                    f.write(f'    {src_id}["{src}"] --> {tgt_id}["{tgt}"]\n')
                    written_nodes.add(src_id)
                    written_nodes.add(tgt_id)
        # Add isolated nodes (no outgoing edges and not targeted by any edge)
        targets_all = set()
        for targets in dependencies.values():
            targets_all.update(targets)
        isolated = nodes - targets_all - set(k for k, v in dependencies.items() if v)
        for src in sorted(isolated):
            src_id = to_id(src)
            if src_id not in written_nodes:
                f.write(f'    {src_id}["{src}"]\n')
                written_nodes.add(src_id)
        f.write('```\n')


def main():
    parser = argparse.ArgumentParser(description='FileFlow: Output Python file import dependencies as Markdown.')
    parser.add_argument('project_dir', help='Root directory of Python project')
    parser.add_argument('--output', default='fileflow_output.md', help='Output Markdown file path (default: fileflow_output.md)')
    args = parser.parse_args()

    py_files = find_py_files(args.project_dir)
    if not py_files:
        print("[FileFlow] ERROR: No Python files found in the specified directory.")
        return
    dependencies, module_to_file = build_dependency_graph(py_files, args.project_dir)
    write_markdown(dependencies, args.output)
    print(f"[FileFlow] Dependency report saved to {args.output}")


if __name__ == '__main__':
    main()
