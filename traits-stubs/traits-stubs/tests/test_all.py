from pathlib import Path
from unittest import TestCase

import pkg_resources

from util import MypyAssertions

examples_dir = Path(
    pkg_resources.resource_filename('traits-stubs', 'tests/examples'))


class TestAnnotations(TestCase, MypyAssertions):
    def test_all(self):
        for file_path in examples_dir.glob("*.py"):
            with self.subTest(file_path=file_path):
                self.assertRaisesMypyError(file_path)
