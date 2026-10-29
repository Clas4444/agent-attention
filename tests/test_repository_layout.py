"""Live navigation, naming and historical-data preservation across path moves."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class RepositoryLayoutTests(unittest.TestCase):
    def test_live_relative_markdown_links_resolve(self):
        pages = [ROOT/'README.md',ROOT/'benchmarks/README.md',*sorted((ROOT/'docs').rglob('*.md')),
                 *sorted((ROOT/'skills').rglob('*.md'))]
        for page in pages:
            for target in re.findall(r'\]\(([^)]+)\)',page.read_text(encoding='utf-8')):
                parts = urlsplit(target)
                if parts.scheme or parts.netloc or not parts.path:
                    continue
                with self.subTest(page=page.relative_to(ROOT).as_posix(),target=target):
                    self.assertTrue((page.parent/unquote(parts.path)).exists())

    def test_document_and_python_names_follow_conventions(self):
        for path in (ROOT/'docs').rglob('*'):
            if path.is_file() and path.name!='README.md':
                with self.subTest(path=path.relative_to(ROOT).as_posix()):
                    self.assertRegex(path.stem,r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
        for path in [*(ROOT/'scripts').rglob('*.py'),*(ROOT/'tests').rglob('*.py')]:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertRegex(path.stem,r'^[a-z_][a-z0-9_]*$')

    def test_historical_json_and_report_bodies_are_preserved(self):
        manifest=json.loads((ROOT/'docs/development/path-migrations.json').read_text(encoding='utf-8'))
        for name,expected in manifest['preserved_report_sha256'].items():
            with self.subTest(path=name):
                self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),expected)
        for name,expected in manifest['preserved_report_text_sha256'].items():
            with self.subTest(path=name):
                body=re.sub(r'\]\([^)]+\)','](<link>)',(ROOT/name).read_text(encoding='utf-8'))
                self.assertEqual(hashlib.sha256(body.encode()).hexdigest(),expected)

    def test_migration_destinations_and_stable_entrypoints_exist(self):
        manifest=json.loads((ROOT/'docs/development/path-migrations.json').read_text(encoding='utf-8'))
        for name in [*manifest['paths'].values(),*manifest['compatibility_entrypoints'],
                     manifest['canonical_generator_entrypoint']]:
            with self.subTest(path=name): self.assertTrue((ROOT/name).is_file())
