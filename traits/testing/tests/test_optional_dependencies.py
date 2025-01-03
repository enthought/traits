# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.testing.optional_dependencies import optional_import


class TestImportHandler(unittest.TestCase):
    def test_import_succeeds(self):

        module = optional_import("itertools")
        self.assertEqual(module.__name__, "itertools")

    def test_import_fails(self):

        module = optional_import("unavailable_module")
        self.assertIsNone(module)
