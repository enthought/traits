# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
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

from traits.api import BaseInt, Either, HasTraits, Int, Tuple
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
