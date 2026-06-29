#!/usr/bin/env python3
"""
PostToolUse(Read) hook — when Claude reads an OKF file, inject its linked concepts.
Receives tool call JSON via stdin, outputs additionalContext JSON.
"""
import sys
import os
import re
import json

SILENT = '{"continue": true}'

OKF_CANDIDATES = ('.lore', '.okf', 'okf', 'knowledge', '.second-brain', 'brain')


def parse_frontmatter(content):
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ':' in line:
            k, _, v = line.partition(':')
            fm[k.strip()] = v.strip().strip('"\'')
    return fm


def find_okf_dir(file_path, project_root):
    abs_file = os.path.realpath(file_path)
    for name in OKF_CANDIDATES:
        okf_dir = os.path.realpath(os.path.join(project_root, name))
        if abs_file.startswith(okf_dir + os.sep):
            return okf_dir, name
    return None, None


def extract_md_links(content, base_dir):
    links = re.findall(r'\[[^\]]+\]\(([^)]+\.md)\)', content)
    result = []
    for href in links:
        if href.startswith('http'):
            continue
        abs_path = os.path.realpath(os.path.join(base_dir, href))
        if os.path.isfile(abs_path):
            result.append(abs_path)
    return result[:10]  # ponytail: cap at 10 to stay fast


def emit(context):
    escaped = context.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    is_cursor = bool(os.environ.get('CURSOR_PLUGIN_ROOT'))
    is_claude = bool(os.environ.get('CLAUDE_PLUGIN_ROOT')) and not os.environ.get('COPILOT_CLI')
    if is_cursor:
        print(f'{{"additional_context": "{escaped}"}}')
    elif is_claude:
        print(f'{{"hookSpecificOutput": {{"hookEventName": "PostToolUse", "additionalContext": "{escaped}"}}}}')
    else:
        print(f'{{"additionalContext": "{escaped}"}}')


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        print(SILENT)
        return

    if payload.get('tool_name') != 'Read':
        print(SILENT)
        return

    file_path = payload.get('tool_input', {}).get('file_path', '')
    if not file_path or not file_path.endswith('.md'):
        print(SILENT)
        return

    project_root = os.getcwd()
    okf_dir, _ = find_okf_dir(file_path, project_root)
    if not okf_dir:
        print(SILENT)
        return

    try:
        with open(file_path, encoding='utf-8', errors='replace') as f:
            content = f.read(8000)
    except Exception:
        print(SILENT)
        return

    linked_paths = extract_md_links(content, os.path.dirname(os.path.abspath(file_path)))
    if not linked_paths:
        print(SILENT)
        return

    lines = ["Linked concepts:"]
    for abs_path in linked_paths:
        try:
            with open(abs_path, encoding='utf-8', errors='replace') as f:
                linked_content = f.read(2000)
            fm = parse_frontmatter(linked_content)
            rel = os.path.relpath(abs_path, okf_dir)
            typ = f" [{fm['type']}]" if fm.get('type') else ''
            desc = f" — {fm.get('description', '')[:80]}" if fm.get('description') else ''
            lines.append(f"  {rel}{typ}{desc}")
        except Exception:
            pass

    if len(lines) <= 1:
        print(SILENT)
        return

    emit('\n'.join(lines))


if __name__ == '__main__':
    main()
