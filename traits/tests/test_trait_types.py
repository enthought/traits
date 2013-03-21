#-------------------------------------------------------------------------------
#
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
#-------------------------------------------------------------------------------

""" Unit test case for testing trait types created by subclassing TraitType.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.testing.unittest_tools import unittest

from traits.api import Float, TraitType

#-------------------------------------------------------------------------------
#  'TraitTypesTest' unit test class:
#-------------------------------------------------------------------------------

class TraitTypesTest ( unittest.TestCase ):

    #---------------------------------------------------------------------------
    #  Test fixture set-up:
    #---------------------------------------------------------------------------

    def setUp ( self ):
        """ Test fixture set-up.
        """
        pass

    #---------------------------------------------------------------------------
    #  Test fixture tear-down:
    #---------------------------------------------------------------------------

    def tearDown ( self ):
        """ Test fixture tear-down.
        """
        pass

    #---------------------------------------------------------------------------
    #  Individual unit test methods:
    #---------------------------------------------------------------------------

    def test_ ( self ):
        pass

    def test_traits_shared_transient(self):
        # Regression test for a bug in traits where the same _metadata
        # dictionary was shared between different trait types.
        class LazyProperty(TraitType):
            def get(self, obj, name):
                return 1729

        self.assertFalse(Float().transient)
        LazyProperty().as_ctrait()
        self.assertFalse(Float().transient)


# Run the unit tests (if invoked from the command line):
if __name__ == '__main__':
    unittest.main()

