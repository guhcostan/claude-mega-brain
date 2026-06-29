#!/usr/bin/env python3
"""Scan project root for OKF concepts (any .md with type: frontmatter) and print a compact index."""
import sys
import os
import re
import json

SKIP_DIRS = {
    'node_modules', '.git', '.cache', 'vendor', 'dist', 'build',
    '__pycache__', '.venv', 'venv', '.tox', 'coverage', '.nyc_output',
    'target', '.gradle', 'Pods', '.dart_tool', '.flutter-plugins',
}


def parse_frontmatter(content):
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?', content, re.DOTALL)
    if not m:
        return {}, 0
    fm = {}
    for line in m.group(1).splitlines():
        if ':' in line:
            k, _, v = line.partition(':')
            fm[k.strip()] = v.strip().strip('"\'')
    return fm, m.end()


def body_excerpt(content, fm_end):
    body = content[fm_end:].strip()
    body = re.sub(r'^#+[^\n]+\n', '', body, flags=re.MULTILINE).strip()
    body = re.sub(r'^\|.+', '', body, flags=re.MULTILINE).strip()
    m = re.match(r'([^.\n!?]{10,}[.!?])', body)
    if m:
        return m.group(1).strip()[:100]
    first = body.split('\n')[0].strip()
    return first[:100] if len(first) > 10 else ''


def last_log_entries(log_path, n=3):
    try:
        with open(log_path, encoding='utf-8', errors='replace') as f:
            content = f.read()
        m = re.match(r'^---\s*\n.*?\n---\s*\n', content, re.DOTALL)
        body = content[m.end():] if m else content
        lines = [l.strip() for l in body.splitlines() if l.strip() and not l.startswith('#')]
        return lines[-n:]
    except Exception:
        return []


def load_config(project_root):
    try:
        with open(os.path.join(project_root, '.mega-brain.json')) as f:
            return json.load(f)
    except Exception:
        return {}


def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    project_root = sys.argv[1]
    cfg = load_config(project_root)
    max_concepts = int(cfg.get('maxConcepts', 60))
    priority_types = cfg.get('priorityTypes', [])
    extra_skip = set(cfg.get('exclude', []))
    skip = SKIP_DIRS | extra_skip

    concepts = []
    log_entries = []

    for root, dirs, files in os.walk(project_root):
        # prune skip dirs in-place
        dirs[:] = sorted(d for d in dirs if d not in skip and not d.startswith('.cache'))

        for fname in sorted(files):
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, project_root)

            if fname == 'log.md' and not log_entries:
                log_entries = last_log_entries(fpath)
                continue

            try:
                with open(fpath, encoding='utf-8', errors='replace') as f:
                    content = f.read(4000)
                fm, fm_end = parse_frontmatter(content)
                if not fm.get('type') and fname != 'index.md':
                    continue
                desc = fm.get('description', '') or body_excerpt(content, fm_end)
                concepts.append({
                    'path': rel,
                    'type': fm.get('type', ''),
                    'desc': desc[:100],
                    'is_index': fname == 'index.md',
                    'priority': priority_types.index(fm.get('type', '')) if fm.get('type') in priority_types else 999,
                })
            except Exception:
                pass

    concepts.sort(key=lambda c: (0 if c['is_index'] else 1, c['priority'], c['path']))

    count = len(concepts)
    lines = [
        f"Knowledge: {count} documented concept{'s' if count != 1 else ''} found in project",
        "Concepts with `type:` frontmatter — read any file for full details.",
    ]

    if log_entries:
        lines += ["", "Recent (log.md):"] + [f"  {e}" for e in log_entries]

    lines.append("")
    for c in concepts[:max_concepts]:
        typ = f" [{c['type']}]" if c['type'] else ''
        desc = f" — {c['desc']}" if c['desc'] else ''
        lines.append(f"  {c['path']}{typ}{desc}")

    if count > max_concepts:
        lines.append(f"  ... +{count - max_concepts} more")

    print('\n'.join(lines))


if __name__ == '__main__':
    main()
