# -----------------------------------------------------------------------------
#
#  Copyright (c) 2019, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
# -----------------------------------------------------------------------------

import sys
from types import ModuleType
import unittest

from traits.testing.optional_dependencies import optional_import


class MockModule(ModuleType):
    """Mock module as object for testing"""
    pass


# Assign to sys modules to allow import
sys.modules['mock_module'] = MockModule(name='mock')


class TestImportHandler(unittest.TestCase):

    def test_import_succeeds(self):

        module = optional_import('mock_module')
        self.assertEqual(module.__name__, 'mock')

    def test_import_fails(self):

        module = optional_import('unavailable_module')
        self.assertIsNone(module)
