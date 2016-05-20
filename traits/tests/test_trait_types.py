#  Unit test case for testing trait types created by subclassing TraitType.
#
#  Written by: David C. Morrill
#
#  Date: 4/10/2007
#
#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#

""" Unit test case for testing trait types created by subclassing TraitType.
"""

from traits.testing.unittest_tools import unittest

from traits.api import Float, TraitType


class TraitTypesTest(unittest.TestCase):

    def test_traits_shared_transient(self):
        # Regression test for a bug in traits where the same _metadata
        # dictionary was shared between different trait types.
        class LazyProperty(TraitType):
            def get(self, obj, name):
                return 1729

        self.assertFalse(Float().transient)
        LazyProperty().as_ctrait()
        self.assertFalse(Float().transient)

    def test_numpy_validators_loaded_if_numpy_present(self):
        # If 'numpy' is available, the numpy validators should be loaded.

        # Make sure that numpy is present on this machine.
        try:
            import numpy
        except ImportError:
            self.skipTest("numpy library not found.")

        # Remove numpy from the list of imported modules.
        import sys
        del sys.modules['numpy']
        for k in list(sys.modules):
            if k.startswith('numpy.'):
                del sys.modules[k]

        # Check that the validators contain the numpy types.
        from traits.trait_types import float_fast_validate
        import numpy
        self.assertIn(numpy.floating, float_fast_validate)


# Run the unit tests (if invoked from the command line):
if __name__ == '__main__':
    unittest.main()
