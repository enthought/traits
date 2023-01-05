# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Unit tests for the Tuple trait type.
"""
import unittest

from traits.api import (
    BaseInt, Either, HasTraits, Int, List, Str, TraitError, Tuple)
from traits.tests.tuple_test_mixin import TupleTestMixin


class BadInt(BaseInt):
    """ Test class used to simulate a Tuple item with bad validation.
    """

    # Describe the trait type
    info_text = 'a bad integer'

    def validate(self, object, name, value):
        # Simulate a coding error in the validation method
        return 1 / 0


class TupleTestCase(TupleTestMixin, unittest.TestCase):
    def setUp(self):
        self.trait = Tuple

    def test_unexpected_validation_exceptions_are_propagated(self):
        # Regression test for enthought/traits#1389.
        class A(HasTraits):
            foo = Tuple(BadInt(), BadInt())

            bar = Either(Int, Tuple(BadInt(), BadInt()))

        a = A()
        with self.assertRaises(ZeroDivisionError):
            a.foo = (3, 5)

        with self.assertRaises(ZeroDivisionError):
            a.bar = (3, 5)

    def test_non_constant_defaults(self):
        class A(HasTraits):
            foo = Tuple(List(Int),)

        a = A()
        a.foo[0].append(35)
        self.assertEqual(a.foo[0], [35])

        # The inner list should be being validated.
        with self.assertRaises(TraitError):
            a.foo[0].append(3.5)

        # The inner list should not be shared between instances.
        b = A()
        self.assertEqual(b.foo[0], [])

    def test_constant_defaults(self):
        # Exercise the code path where all child traits have a constant
        # default type.
        class A(HasTraits):
            foo = Tuple(Int, Tuple(Str, Int))

        a = A()
        b = A()
        self.assertEqual(a.foo, (0, ("", 0)))
        self.assertIs(a.foo, b.foo)

    def test_lists_not_accepted(self):

        class A(HasTraits):
            foo = Tuple(Int(), Int())

        a = A()
        with self.assertRaises(TraitError):
            a.foo = [2, 3]

    def test_deprecated_list_validation(self):
        class A(HasTraits):
            foo = Tuple()

        a = A()
        with self.assertWarns(DeprecationWarning):
            a.foo = [2, 3]

        self.assertEqual(a.foo, (2, 3))
