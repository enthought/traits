# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tests for the PrefixList handler.
"""

import pickle
import unittest

from traits.api import HasTraits, TraitError, PrefixList


class TestPrefixList(unittest.TestCase):
    def test_assignment(self):
        class A(HasTraits):
            foo = PrefixList(["zero", "one", "two"], default_value="one")

        a = A()

        a.foo = 'z'
        self.assertEqual(a.foo, "zero")

        with self.assertRaises(TraitError) as exception_context:
            a.foo = ''
        self.assertIn(
            "The 'foo' trait of an A instance must be 'zero' or 'one' or 'two'"
            " (or any unique prefix), but a value of ''",
            str(exception_context.exception),
        )

    def test_bad_types(self):
        class A(HasTraits):
            foo = PrefixList(["zero", "one", "two"], default_value="one")

        a = A()

        wrong_type = [[], (1, 2, 3), 1j, 2.3, 23, b"zero", None]
        for value in wrong_type:
            with self.subTest(value=value):
                with self.assertRaises(TraitError):
                    a.foo = value

    def test_repeated_prefix(self):
        class A(HasTraits):
            foo = PrefixList(("abc1", "abc2"))

        a = A()

        a.foo = "abc1"
        self.assertEqual(a.foo, "abc1")

        with self.assertRaises(TraitError):
            a.foo = "abc"

    def test_default_default(self):
        class A(HasTraits):
            foo = PrefixList(["zero", "one", "two"], default_value="zero")

        a = A()
        self.assertEqual(a.foo, "zero")

    def test_explicit_default(self):
        class A(HasTraits):
            foo = PrefixList(["zero", "one", "two"], default_value="one")

        a = A()
        self.assertEqual(a.foo, "one")

    def test_default_subject_to_completion(self):
        class A(HasTraits):
            foo = PrefixList(["zero", "one", "two"], default_value="o")

        a = A()
        self.assertEqual(a.foo, "one")

    def test_default_subject_to_validation(self):
        with self.assertRaises(ValueError):

            class A(HasTraits):
                foo = PrefixList(["zero", "one", "two"], default_value="uno")

    def test_default_legal_but_not_unique_prefix(self):
        # Corner case to exercise internal logic: the default is not a unique
        # prefix, but it is one of the list of values, so it's legal.
        class A(HasTraits):
            foo = PrefixList(["live", "modal", "livemodal"], default="live")

        a = A()
        self.assertEqual(a.foo, "live")

    def test_default_value_cant_be_passed_by_position(self):
        with self.assertRaises(TypeError):
            PrefixList(["zero", "one", "two"], "one")

    def test_values_not_sequence(self):
        # Defining values with this signature is not supported
        with self.assertRaises(TypeError):
            PrefixList("zero", "one", "two")

    def test_values_not_all_iterables(self):
        # Make sure we don't confuse other sequence types, e.g. str
        with self.assertRaises(TypeError) as exception_context:
            PrefixList("zero")

        self.assertEqual(
            str(exception_context.exception),

            "values should be a collection of strings, not 'zero'"
        )

    def test_values_is_empty(self):
        # it doesn't make sense to use a PrefixList with an empty list, so make
        # sure we raise a ValueError
        with self.assertRaises(ValueError):
            PrefixList([])

    def test_values_is_empty_with_default_value(self):
        # Raise even if we give a default value.
        with self.assertRaises(ValueError):
            PrefixList([], default_value="one")

    def test_no_nested_exception(self):
        # Regression test for enthought/traits#1155
        class A(HasTraits):
            foo = PrefixList(["zero", "one", "two"])

        a = A()
        try:
            a.foo = "three"
        except TraitError as exc:
            self.assertIsNone(exc.__context__)
            self.assertIsNone(exc.__cause__)

    def test_pickle_roundtrip(self):
        class A(HasTraits):
            foo = PrefixList(["zero", "one", "two"], default_value="one")

        a = A()
        foo_trait = a.traits()["foo"]
        reconstituted = pickle.loads(pickle.dumps(foo_trait))

        self.assertEqual(
            foo_trait.validate(a, "foo", "ze"),
            "zero",
        )
        with self.assertRaises(TraitError):
            foo_trait.validate(a, "foo", "zero-knowledge")

        self.assertEqual(
            reconstituted.validate(a, "foo", "ze"),
            "zero",
        )
        with self.assertRaises(TraitError):
            reconstituted.validate(a, "foo", "zero-knowledge")
