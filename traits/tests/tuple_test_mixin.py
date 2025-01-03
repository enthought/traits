# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import HasTraits, TraitError
from traits.testing.unittest_tools import UnittestTools

VALUES = ("value1", 33, None)


class TupleTestMixin(UnittestTools):
    """ A mixin class for testing tuple like traits.

    TestCases should set the self.trait attribute during setUp for the tests
    to run.

    """

    def test_default_values(self):
        # Check that the default values for t1 and t2 are correctly
        # derived from the VALUES tuple.

        dummy = self._create_class()
        self.assertEqual(dummy.t1, VALUES)
        self.assertEqual(dummy.t2, VALUES)

    def test_simple_assignment(self):
        # Check that we can assign different values of the correct type.

        dummy = self._create_class()
        with self.assertTraitChanges(dummy, "t1"):
            dummy.t1 = ("other value 1", 77, None)
        with self.assertTraitChanges(dummy, "t2"):
            dummy.t2 = ("other value 2", 99, None)

    def test_invalid_assignment_length(self):
        # Check that assigning a tuple of incorrect length
        # raises a TraitError.
        self._assign_invalid_values_length(("str", 44))
        self._assign_invalid_values_length(("str", 33, None, []))

    def test_type_checking(self):
        # Test that type checking is done for the 't1' attribute.
        dummy = self._create_class()
        other_tuple = ("other value", 75, True)
        with self.assertRaises(TraitError):
            dummy.t1 = other_tuple
        self.assertEqual(dummy.t1, VALUES)

        # Test that no type checking is done for the 't2' attribute.
        try:
            dummy.t2 = other_tuple
        except TraitError:
            self.fail("Unexpected TraitError when assigning to tuple.")
        self.assertEqual(dummy.t2, other_tuple)

    def _assign_invalid_values_length(self, values):
        dummy = self._create_class()
        with self.assertRaises(TraitError):
            dummy.t1 = values
        self.assertEqual(dummy.t1, VALUES)
        with self.assertRaises(TraitError):
            dummy.t2 = values
        self.assertEqual(dummy.t2, VALUES)

    def _create_class(self):
        trait = self.trait

        class Dummy(HasTraits):

            t1 = trait(VALUES)

            t2 = trait(*VALUES)

        return Dummy()
