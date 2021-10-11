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
Tests for the PrefixMap handler.
"""

import pickle
import unittest

from traits.api import HasTraits, Int, PrefixMap, TraitError


class Person(HasTraits):
    married = PrefixMap({"yes": 1, "yeah": 1, "no": 0, "nah": 0})


class TestPrefixMap(unittest.TestCase):
    def test_assignment(self):
        person = Person()

        # Test prefix
        person.married = "yea"
        self.assertEqual("yeah", person.married)
        self.assertEqual(1, person.married_)

        person.married = "yes"
        self.assertEqual("yes", person.married)
        self.assertEqual(1, person.married_)

        person.married = "na"
        self.assertEqual("nah", person.married)
        self.assertEqual(0, person.married_)

        with self.assertRaises(TraitError):
            person.married = "unknown"

        # Test duplicate prefix
        with self.assertRaises(TraitError):
            person.married = "ye"

    def test_bad_types(self):
        person = Person()

        wrong_type = [[], (1, 2, 3), 1j, 2.3, 23, b"not a string", None]
        for value in wrong_type:
            with self.subTest(value=value):
                with self.assertRaises(TraitError):
                    person.married = value

    def test_no_default(self):
        mapping = {"yes": 1, "yeah": 1, "no": 0, "nah": 0}

        class Person(HasTraits):
            married = PrefixMap(mapping)

        p = Person()

        # Since we're using Python >= 3.6, we can rely on dictionaries
        # being ordered, and then the default is predictable.
        self.assertEqual(p.married, "yes")
        self.assertEqual(p.married_, 1)

    def test_default(self):
        class Person(HasTraits):
            married = PrefixMap({"yes": 1, "yeah": 1, "no": 0, "nah": 0},
                                default_value="nah")
        p = Person()
        self.assertEqual(p.married, "nah")
        self.assertEqual(p.married_, 0)

    def test_default_keyword_only(self):
        with self.assertRaises(TypeError):
            PrefixMap({"yes": 1, "no": 0}, "yes")

    def test_default_method(self):
        class Person(HasTraits):
            married = PrefixMap({"yes": 1, "yeah": 1, "no": 0, "nah": 0})

            default_calls = Int(0)

            def _married_default(self):
                self.default_calls += 1
                return "nah"

        p = Person()
        self.assertEqual(p.married, "nah")
        self.assertEqual(p.married_, 0)
        self.assertEqual(p.default_calls, 1)

        # Check that the order doesn't matter
        p2 = Person()
        self.assertEqual(p2.married_, 0)
        self.assertEqual(p2.married, "nah")
        self.assertEqual(p2.default_calls, 1)

    def test_default_static_override_static(self):
        class BasePerson(HasTraits):
            married = PrefixMap({"yes": 1, "yeah": 1, "no": 0, "nah": 0},
                                default_value="nah")

        class Person(BasePerson):
            married = "yes"

        p = Person()
        self.assertEqual(p.married, "yes")
        self.assertEqual(p.married_, 1)

    def test_default_static_override_method(self):
        class BasePerson(HasTraits):
            married = PrefixMap({"yes": 1, "yeah": 1, "no": 0, "nah": 0},
                                default_value="nah")

        class Person(BasePerson):
            default_calls = Int(0)

            def _married_default(self):
                self.default_calls += 1
                return "yes"

        p = Person()
        self.assertEqual(p.married, "yes")
        self.assertEqual(p.married_, 1)
        self.assertEqual(p.default_calls, 1)

    def test_default_method_override_static(self):
        class BasePerson(HasTraits):
            married = PrefixMap({"yes": 1, "yeah": 1, "no": 0, "nah": 0})

            default_calls = Int(0)

            def _married_default(self):
                self.default_calls += 1
                return "nah"

        class Person(BasePerson):
            married = "yes"

        p = Person()
        self.assertEqual(p.married, "yes")
        self.assertEqual(p.married_, 1)
        self.assertEqual(p.default_calls, 0)

    def test_default_method_override_method(self):
        class BasePerson(HasTraits):
            married = PrefixMap({"yes": 1, "yeah": 1, "no": 0, "nah": 0})

            default_calls = Int(0)

            def _married_default(self):
                self.default_calls += 1
                return "nah"

        class Person(BasePerson):
            def _married_default(self):
                self.default_calls += 1
                return "yes"

        p = Person()
        self.assertEqual(p.married, "yes")
        self.assertEqual(p.married_, 1)
        self.assertEqual(p.default_calls, 1)

    def test_static_default_transformed(self):
        # Test the static default is transformed
        class Person(HasTraits):
            married = PrefixMap(
                {"yes": 1, "yeah": 1, "no": 0}, default_value="yea")

        p = Person()
        self.assertEqual(p.married, "yeah")
        self.assertEqual(p.married_, 1)

        # access mapped trait first is okay
        p = Person()
        self.assertEqual(p.married_, 1)
        self.assertEqual(p.married, "yeah")

    def test_static_default_validation_error(self):
        with self.assertRaises(ValueError):
            class Person(HasTraits):
                married = PrefixMap(
                    {"yes": 1, "yeah": 1, "no": 0}, default_value="meh")

    def test_no_nested_exception(self):
        # Regression test for enthought/traits#1155
        class A(HasTraits):
            washable = PrefixMap({"yes": 1, "no": 0})

        a = A()
        try:
            a.washable = "affirmatron"
        except TraitError as exc:
            self.assertIsNone(exc.__context__)
            self.assertIsNone(exc.__cause__)

    def test_pickle_roundtrip(self):
        class Person(HasTraits):
            married = PrefixMap({"yes": 1, "yeah": 1, "no": 0, "nah": 0},
                                default_value="yea")

        p = Person()
        married_trait = p.traits()["married"]
        reconstituted = pickle.loads(pickle.dumps(married_trait))

        self.assertEqual(married_trait.validate(p, "married", "yea"), "yeah")

        self.assertEqual(reconstituted.validate(p, "married", "yea"), "yeah")

        with self.assertRaises(TraitError):
            reconstituted.validate(p, "married", "uknown")

        with self.assertRaises(TraitError):
            reconstituted.validate(p, "married", "ye")

    def test_empty_map(self):
        with self.assertRaises(ValueError):
            PrefixMap({})

    def test_pickle_shadow_trait(self):
        class Person(HasTraits):
            married = PrefixMap({"yes": 1, "yeah": 1, "no": 0, "nah": 0},
                                default_value="yeah")

        p = Person()
        married_shadow_trait = p.trait("married_")
        reconstituted = pickle.loads(pickle.dumps(married_shadow_trait))

        default_value_callable = reconstituted.default_value()[1]

        self.assertEqual(default_value_callable(p), 1)

    def test_existence_of__map(self):
        # This test can be removed once Mayavi no longer depends on the
        # existence of the _map attribute.
        # xref: enthought/traits#1577
        # xref: enthought/mayavi#1094

        prefix_map = PrefixMap({"yes": 1, "yeah": 1, "no": 0, "nah": 0})
        self.assertEqual(prefix_map._map["yes"], "yes")
