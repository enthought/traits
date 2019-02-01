""" Tests for the import manager. """

import unittest

from traits.util.api import import_symbol


class TestImportSymbol(unittest.TestCase):
    """ Tests for the import manager. """

    def test_import_dotted_symbol(self):
        """ import dotted symbol """

        import tarfile

        symbol = import_symbol("tarfile.TarFile")
        self.assertEqual(symbol, tarfile.TarFile)

        return

    def test_import_nested_symbol(self):
        """ import nested symbol """

        import tarfile

        symbol = import_symbol("tarfile:TarFile.open")
        self.assertEqual(symbol, tarfile.TarFile.open)

        return

    def test_import_dotted_module(self):
        """ import dotted module """

        symbol = import_symbol("traits.util.import_symbol:import_symbol")

        self.assertEqual(symbol, import_symbol)

        return
