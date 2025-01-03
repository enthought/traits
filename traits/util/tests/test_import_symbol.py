# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

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

    def test_import_nested_symbol(self):
        """ import nested symbol """

        import tarfile

        symbol = import_symbol("tarfile:TarFile.open")
        self.assertEqual(symbol, tarfile.TarFile.open)

    def test_import_dotted_module(self):
        """ import dotted module """

        symbol = import_symbol("traits.util.import_symbol:import_symbol")

        self.assertEqual(symbol, import_symbol)
