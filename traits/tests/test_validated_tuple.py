#------------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#------------------------------------------------------------------------------
from traits.api import HasStrictTraits, Int, TraitError
from traits.tests import test_tuple
from traits.trait_types import ValidatedTuple

class Simple(HasStrictTraits):

    scalar_range = ValidatedTuple(
        Int(0), Int(1), validation=lambda x: x[0] < x[1])


class TestValidatedTuple(test_tuple.TestTuple):

    def test_initialization(self):
        simple = Simple()
        self.assertEqual(simple.scalar_range, (0, 1))

    def test_invalid_definition(self):
        with self.assertRaises(TraitError):
            class InValidSimple(HasStrictTraits):
                scalar_range = ValidatedTuple(
                    Int(1), Int(0), validation=lambda x: x[0] < x[1])

    def test_custom_validation(self):
        simple = Simple()

        # This should pass
        simple.scalar_range = (2, 5)
        self.assertEqual(simple.scalar_range, (2, 5))

        with self.assertRaises(TraitError):
            # This should raise
            simple.scalar_range = (5, 2)
