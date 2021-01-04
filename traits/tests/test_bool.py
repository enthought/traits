# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tests for the Bool trait type.
"""
import unittest

from traits.api import Bool, Dict, HasTraits, Int, TraitError
from traits.testing.optional_dependencies import numpy, requires_numpy


class A(HasTraits):
    foo = Bool


class TestBool(unittest.TestCase):
    def test_default_value(self):
        a = A()
        # We should get something of exact type bool.
        self.assertEqual(type(a.foo), bool)
        self.assertFalse(a.foo)

    def test_accepts_bool(self):
        a = A()
        a.foo = True
        self.assertTrue(a.foo)
        a.foo = False
        self.assertFalse(a.foo)

    def test_does_not_accept_int_or_float(self):
        a = A()

        bad_values = [-1, "a string", 1.0]
        for bad_value in bad_values:
            with self.assertRaises(TraitError):
                a.foo = bad_value

        # Double check that foo didn't actually change
        self.assertEqual(type(a.foo), bool)
        self.assertFalse(a.foo)

    @requires_numpy
    def test_accepts_numpy_bool(self):
        # A bool trait should accept a NumPy bool_.
        a = A()
        a.foo = numpy.bool_(True)
        self.assertTrue(a.foo)

    @requires_numpy
    def test_numpy_bool_retrieved_as_bool(self):
        a = A()
        a.foo = numpy.bool_(True)
        self.assertIsInstance(a.foo, bool)

        a.foo = numpy.bool_(False)
        self.assertIsInstance(a.foo, bool)

    @requires_numpy
    def test_numpy_bool_accepted_as_dict_value(self):
        # Regression test for enthought/traits#299.
        class HasBoolDict(HasTraits):
            foo = Dict(Int, Bool)

        has_bool_dict = HasBoolDict()
        has_bool_dict.foo[1] = numpy.bool_(True)
        self.assertTrue(has_bool_dict.foo[1])

    @requires_numpy
    def test_numpy_bool_accepted_as_dict_key(self):
        # Regression test for enthought/traits#299.
        class HasBoolDict(HasTraits):
            foo = Dict(Bool, Int)

        has_bool_dict = HasBoolDict()
        key = numpy.bool_(True)
        has_bool_dict.foo[key] = 1
        self.assertEqual(has_bool_dict.foo[key], 1)
