"""Tests of stdlib-only agent tools."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class ToolsTest(unittest.TestCase):
    def test_api_schema_accepts_source_confirmed(self):
        validator = load('validate_api')
        sample = {'schema_version': 1, 'id': 'sample', 'mod': 'sample',
                  'version': '1', 'minecraft': '1.21.1',
                  'source_url': 'https://example.invalid', 'source_commit': 'abcd',
                  'interfaces': [{'name': 'mod', 'kind': 'global', 'methods': [
                      {'name': 'f', 'arguments': ['number'], 'returns': ['boolean'],
                       'verification': 'source-confirmed', 'source_path': 'Test.java'}]}]}
        self.assertEqual(validator.validate(sample), [])
        sample['interfaces'][0]['methods'][0]['verification'] = 'imaginary'
        self.assertTrue(validator.validate(sample))

    def test_diagnostics(self):
        diagnose = load('diagnose').diagnose
        item = diagnose('Lua: attempt to call a nil value\nerror: cannot find symbol')
        self.assertEqual({m['category'] for m in item['findings']},
                         {'missing_api', 'java_compile'})

    def test_benchmark_runner(self):
        benchmark = load('benchmark')
        report = benchmark.run([{'id': 'ok', 'command': ['python3', '-c', 'print("done")'],
                                 'expected': 'done'}], Path(__file__).parent, 3)
        self.assertEqual(report['passed'], 1)


if __name__ == '__main__':
    unittest.main()
