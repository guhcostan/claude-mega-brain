#!/usr/bin/env python3
"""Tests for claude-mega-brain OKF scripts."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'scripts')
sys.path.insert(0, SCRIPTS_DIR)

from okf_utils import get_project_root, get_scan_root, is_okf_concept, parse_frontmatter


def load_script_module(name, filename):
    path = os.path.join(SCRIPTS_DIR, filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


inject_links = load_script_module('inject_links', 'inject-links.py')


def run_parse_okf(project_root):
    result = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS_DIR, 'parse-okf.py'), project_root],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


class TestOkfUtils(unittest.TestCase):
    def test_parse_frontmatter_basic(self):
        content = "---\ntype: Metric\ntitle: WAU\ndescription: Weekly active users.\n---\n# Body\n"
        fm, end = parse_frontmatter(content)
        self.assertEqual(fm['type'], 'Metric')
        self.assertEqual(fm['description'], 'Weekly active users.')
        self.assertGreater(end, 0)

    def test_parse_frontmatter_missing(self):
        fm, end = parse_frontmatter("# No frontmatter\n")
        self.assertEqual(fm, {})
        self.assertEqual(end, 0)

    def test_is_okf_concept(self):
        self.assertTrue(is_okf_concept({'type': 'Table'}, 'orders.md'))
        self.assertTrue(is_okf_concept({}, 'index.md'))
        self.assertFalse(is_okf_concept({}, 'notes.md'))

    def test_get_scan_root_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(get_scan_root(tmp, {}), tmp)

    def test_get_scan_root_with_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            knowledge = os.path.join(tmp, 'knowledge')
            os.makedirs(knowledge)
            cfg = {'dir': 'knowledge'}
            self.assertEqual(get_scan_root(tmp, cfg), knowledge)

    def test_get_scan_root_invalid_dir_falls_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = {'dir': '../outside'}
            self.assertEqual(get_scan_root(tmp, cfg), tmp)

    def test_get_project_root_prefers_env(self):
        with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/project/root'}):
            self.assertEqual(get_project_root(), '/project/root')


class TestParseOkf(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__('shutil').rmtree(self.tmp, ignore_errors=True))

    def write(self, rel_path, content):
        full = os.path.join(self.tmp, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w', encoding='utf-8') as f:
            f.write(content)

    def test_finds_concepts_with_type(self):
        self.write('docs/orders.md', "---\ntype: BigQuery Table\ndescription: Order rows.\n---\n")
        out = run_parse_okf(self.tmp)
        self.assertIn('Knowledge: 1 documented concept', out)
        self.assertIn('docs/orders.md [BigQuery Table]', out)

    def test_skips_md_without_type(self):
        self.write('README.md', "# Project\nNo frontmatter.\n")
        out = run_parse_okf(self.tmp)
        self.assertIn('Knowledge: 0 documented concepts', out)

    def test_includes_index_without_type(self):
        self.write('index.md', "# Knowledge map\nCentral reference.\n")
        out = run_parse_okf(self.tmp)
        self.assertIn('index.md', out)

    def test_respects_max_concepts(self):
        for i in range(5):
            self.write(f'c{i}.md', f"---\ntype: Concept\ndescription: Concept {i}.\n---\n")
        with open(os.path.join(self.tmp, '.mega-brain.json'), 'w') as f:
            json.dump({'maxConcepts': 2}, f)
        out = run_parse_okf(self.tmp)
        self.assertIn('... +3 more', out)

    def test_priority_types_order(self):
        self.write('b.md', "---\ntype: Metric\ndescription: B.\n---\n")
        self.write('a.md', "---\ntype: Table\ndescription: A.\n---\n")
        with open(os.path.join(self.tmp, '.mega-brain.json'), 'w') as f:
            json.dump({'priorityTypes': ['Metric', 'Table']}, f)
        out = run_parse_okf(self.tmp)
        metric_pos = out.index('b.md')
        table_pos = out.index('a.md')
        self.assertLess(metric_pos, table_pos)

    def test_exclude_dirs(self):
        self.write('skip/hidden.md', "---\ntype: Concept\ndescription: Hidden.\n---\n")
        with open(os.path.join(self.tmp, '.mega-brain.json'), 'w') as f:
            json.dump({'exclude': ['skip']}, f)
        out = run_parse_okf(self.tmp)
        self.assertIn('Knowledge: 0 documented concepts', out)

    def test_dir_limits_scan(self):
        self.write('inside/knowledge/a.md', "---\ntype: API\ndescription: Inside.\n---\n")
        self.write('outside/b.md', "---\ntype: API\ndescription: Outside.\n---\n")
        with open(os.path.join(self.tmp, '.mega-brain.json'), 'w') as f:
            json.dump({'dir': 'inside/knowledge'}, f)
        out = run_parse_okf(self.tmp)
        self.assertIn('inside/knowledge/a.md', out)
        self.assertNotIn('outside/b.md', out)

    def test_log_entries_injected(self):
        self.write('log.md', "---\ntype: Log\n---\n2026-01-01 — first\n2026-01-02 — second\n")
        self.write('a.md', "---\ntype: Concept\ndescription: A.\n---\n")
        out = run_parse_okf(self.tmp)
        self.assertIn('Recent (log.md):', out)
        self.assertIn('2026-01-02 — second', out)


class TestInjectLinks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__('shutil').rmtree(self.tmp, ignore_errors=True))

    def write(self, rel_path, content):
        full = os.path.join(self.tmp, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w', encoding='utf-8') as f:
            f.write(content)

    def run_hook(self, file_path):
        payload = json.dumps({
            'tool_name': 'Read',
            'tool_input': {'file_path': file_path},
        })
        with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': self.tmp}, clear=False):
            with patch('sys.stdin', StringIO(payload)):
                with patch('sys.stdout', new_callable=StringIO) as stdout:
                    inject_links.main()
                    return stdout.getvalue()

    def test_injects_linked_concepts(self):
        self.write('customers.md', "---\ntype: BigQuery Table\ndescription: Customer profiles.\n---\n")
        self.write('orders.md', (
            "---\ntype: BigQuery Table\ndescription: Order rows.\n---\n"
            "Joined with [customers](customers.md).\n"
        ))
        out = self.run_hook(os.path.join(self.tmp, 'orders.md'))
        self.assertIn('Linked concepts:', out)
        self.assertIn('customers.md', out)

    def test_silent_for_non_okf_file(self):
        self.write('plain.md', "# Just notes\n")
        out = self.run_hook(os.path.join(self.tmp, 'plain.md'))
        self.assertIn('"continue": true', out)

    def test_silent_for_wrong_tool(self):
        payload = json.dumps({'tool_name': 'Write', 'tool_input': {}})
        with patch('sys.stdin', StringIO(payload)):
            with patch('sys.stdout', new_callable=StringIO) as stdout:
                inject_links.main()
                out = stdout.getvalue()
        self.assertIn('"continue": true', out)


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HOOKS_DIR = os.path.join(REPO_ROOT, 'hooks')


class TestHookConfiguration(unittest.TestCase):
    def read_text(self, rel_path):
        with open(os.path.join(REPO_ROOT, rel_path), encoding='utf-8') as file:
            return file.read()

    def test_manifest_does_not_redeclare_hooks(self):
        with open(os.path.join(REPO_ROOT, '.claude-plugin', 'plugin.json'), encoding='utf-8') as file:
            manifest = json.load(file)
        self.assertNotIn('hooks', manifest)

    def test_post_tool_use_runs_wrapper_then_python_helper(self):
        with open(os.path.join(HOOKS_DIR, 'hooks.json'), encoding='utf-8') as file:
            hooks = json.load(file)
        command = hooks['hooks']['PostToolUse'][0]['hooks'][0]['command']
        self.assertRegex(
            command,
            r'run-hook\.cmd"\s+run-python\s+"\$\{CLAUDE_PLUGIN_ROOT\}/scripts/inject-links\.py"',
        )
        self.assertNotIn('python3', command)

    def test_session_start_uses_python_helper_without_hiding_stderr(self):
        session_start = self.read_text('hooks/session-start')
        self.assertIn('run-python', session_start)
        self.assertNotIn('2>/dev/null', session_start)

    def test_release_uses_current_marketplace_name(self):
        release = self.read_text('.github/workflows/release.yml')
        self.assertIn('/plugin install mega-brain@mega-brain', release)
        self.assertNotIn('/plugin install mega-brain@guhcostan', release)


class TestRunPython(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__('shutil').rmtree(self.tmp, ignore_errors=True))
        self.bin_dir = os.path.join(self.tmp, 'bin')
        os.makedirs(self.bin_dir)
        self.helper = os.path.join(HOOKS_DIR, 'run-python')

    def write_executable(self, name, content):
        path = os.path.join(self.bin_dir, name)
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
        os.chmod(path, 0o755)

    def run_helper(self, args):
        env = dict(os.environ)
        env['PATH'] = self.bin_dir
        return subprocess.run(
            ['/bin/bash', self.helper, *args],
            capture_output=True,
            text=True,
            env=env,
        )

    def test_ignores_broken_python3_and_uses_python(self):
        self.write_executable('python3', '#!/bin/sh\nexit 1\n')
        self.write_executable('python', '#!/bin/sh\nif [ "$1" = "--version" ]; then\n  printf "Python fallback\\n"\n  exit 0\nfi\nprintf "python-fallback\\n"\n')

        result = self.run_helper(['-c', 'ignored'])

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, 'python-fallback\n')
        self.assertEqual(result.stderr, '')

    def test_reports_error_when_no_python_interpreter_works(self):
        result = self.run_helper(['-c', 'ignored'])

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('run-python: no working Python interpreter found', result.stderr)


if __name__ == '__main__':
    unittest.main()
