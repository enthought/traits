import unittest

from traits.testing.optional_dependencies import optional_import


class TestImportHandler(unittest.TestCase):
    def test_import_succeeds(self):

        module = optional_import("itertools")
        self.assertEqual(module.__name__, "itertools")

    def test_import_fails(self):

        module = optional_import("unavailable_module")
        self.assertIsNone(module)
