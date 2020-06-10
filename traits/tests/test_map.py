# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tests for the Map handler.
"""

import pickle
import sys
import unittest

from traits.api import HasTraits, Int, List, Map, on_trait_change, TraitError


class Preferences(HasTraits):
    """
    Example class with a Map that records changes to that map.
    """

    # Changes to primary trait of the mapped trait pair
    primary_changes = List()

    # Changes to the shadow trait of the mapped trait pair
    shadow_changes = List()

    color = Map({"red": 4, "green": 2, "yellow": 6}, default_value="yellow")

    @on_trait_change("color")
    def _record_primary_trait_change(self, obj, name, old, new):
        change = obj, name, old, new
        self.primary_changes.append(change)

    @on_trait_change("color_")
    def _record_shadow_trait_change(self, obj, name, old, new):
        change = obj, name, old, new
        self.shadow_changes.append(change)


class TestMap(unittest.TestCase):
    def test_assignment(self):
        class Person(HasTraits):
            married = Map({"yes": 1, "yeah": 1, "no": 0, "nah": 0})

        person = Person()

        person.married = "yes"
        self.assertEqual("yes", person.married)
        self.assertEqual(1, person.married_)

        person.married = "no"
        self.assertEqual("no", person.married)
        self.assertEqual(0, person.married_)

        with self.assertRaises(TraitError):
            person.married = "dont know"

        with self.assertRaises(TraitError):
            person.married = []

    def test_no_default(self):
        mapping = {"yes": 1, "yeah": 1, "no": 0, "nah": 0}

        class Person(HasTraits):
            married = Map(mapping)

        p = Person()
        if sys.version_info >= (3, 6):
            # If we're using Python >= 3.6, we can rely on dictionaries
            # being ordered, and then the default is predictable.
            self.assertEqual(p.married, "yes")
            self.assertEqual(p.married_, 1)
        else:
            # Otherwise, all we can expect is that the default is _one_
            # of the dictionary entries.
            self.assertIn(p.married, mapping)
            self.assertEqual(p.married_, mapping[p.married])

    def test_no_default_reverse_access_order(self):
        mapping = {"yes": 1, "yeah": 1, "no": 0, "nah": 0}

        class Person(HasTraits):
            married = Map(mapping)

        p = Person()
        shadow_value = p.married_
        primary_value = p.married
        if sys.version_info >= (3, 6):
            self.assertEqual(primary_value, "yes")
            self.assertEqual(shadow_value, 1)
        else:
            # For Python < 3.6, dictionary ordering and hence the default
            # value aren't predictable.
            self.assertIn(primary_value, mapping)
            self.assertEqual(shadow_value, mapping[primary_value])

    def test_default(self):
        class Person(HasTraits):
            married = Map({"yes": 1, "yeah": 1, "no": 0, "nah": 0,
                           None: 2}, default_value=None)

        p = Person()
        self.assertIsNone(p.married)
        self.assertEqual(p.married_, 2)

    def test_default_reverse_access_order(self):
        class Person(HasTraits):
            married = Map({"yes": 1, "yeah": 1, "no": 0, "nah": 0,
                           None: 2}, default_value=None)

        p = Person()
        self.assertEqual(p.married_, 2)
        self.assertIsNone(p.married)

    def test_default_method(self):
        class Person(HasTraits):
            married = Map({"yes": 1, "yeah": 1, "no": 0, "nah": 0,
                           None: 2})

            default_calls = Int(0)

            def _married_default(self):
                self.default_calls += 1
                return None

        p = Person()
        self.assertIsNone(p.married)
        self.assertEqual(p.married_, 2)
        self.assertEqual(p.default_calls, 1)

        # Check that the order doesn't matter
        p2 = Person()
        self.assertEqual(p2.married_, 2)
        self.assertIsNone(p2.married)
        self.assertEqual(p2.default_calls, 1)

    def test_default_static_override_static(self):
        class BasePerson(HasTraits):
            married = Map({"yes": 1, "yeah": 1, "no": 0, "nah": 0,
                           None: 2}, default_value=None)

        class Person(BasePerson):
            married = "yes"

        p = Person()
        self.assertEqual(p.married, "yes")
        self.assertEqual(p.married_, 1)

    def test_default_static_override_method(self):
        class BasePerson(HasTraits):
            married = Map({"yes": 1, "yeah": 1, "no": 0, "nah": 0,
                           None: 2}, default_value=None)

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
            married = Map({"yes": 1, "yeah": 1, "no": 0, "nah": 0,
                           None: 2})

            default_calls = Int(0)

            def _married_default(self):
                self.default_calls += 1
                return None

        class Person(BasePerson):
            married = "yes"

        p = Person()
        self.assertEqual(p.married, "yes")
        self.assertEqual(p.married_, 1)
        self.assertEqual(p.default_calls, 0)

    def test_default_method_override_method(self):
        class BasePerson(HasTraits):
            married = Map({"yes": 1, "yeah": 1, "no": 0, "nah": 0,
                           None: 2})

            default_calls = Int(0)

            def _married_default(self):
                self.default_calls += 1
                return None

        class Person(BasePerson):
            def _married_default(self):
                self.default_calls += 1
                return "yes"

        p = Person()
        self.assertEqual(p.married, "yes")
        self.assertEqual(p.married_, 1)
        self.assertEqual(p.default_calls, 1)

    def test_notification(self):

        preferences = Preferences()

        self.assertEqual(len(preferences.primary_changes), 0)
        self.assertEqual(len(preferences.shadow_changes), 0)

        preferences.color = "red"

        self.assertEqual(len(preferences.primary_changes), 1)
        self.assertEqual(len(preferences.shadow_changes), 1)

        preferences.color = "green"

        self.assertEqual(len(preferences.primary_changes), 2)
        self.assertEqual(len(preferences.shadow_changes), 2)

        with self.assertRaises(TraitError):
            preferences.color = "blue"

        self.assertEqual(len(preferences.primary_changes), 2)
        self.assertEqual(len(preferences.shadow_changes), 2)

    def test_notification_init_value(self):

        preferences = Preferences(color="green")

        self.assertEqual(len(preferences.primary_changes), 1)
        self.assertEqual(len(preferences.shadow_changes), 1)

    def test_notification_change_shadow_value(self):

        class PreferencesWithDynamicDefault(Preferences):

            def _color_default(self):
                return "yellow"

        preferences = PreferencesWithDynamicDefault()
        self.assertEqual(len(preferences.primary_changes), 0)
        self.assertEqual(len(preferences.shadow_changes), 0)

        # access the dynamic default of color_ should not trigger event
        # because the value has not changed.
        preferences.color_

        self.assertEqual(len(preferences.primary_changes), 0)
        self.assertEqual(len(preferences.shadow_changes), 0)

    def test_pickle_roundtrip(self):
        class Person(HasTraits):
            married = Map({"yes": 1, "yeah": 1, "no": 0, "nah": 0},
                          default_value="yes")

        p = Person()
        married_trait = p.traits()["married"]
        reconstituted = pickle.loads(pickle.dumps(married_trait))

        self.assertEqual(married_trait.validate(p, "married", "yes"), "yes")

        self.assertEqual(reconstituted.validate(p, "married", "yes"), "yes")

        with self.assertRaises(TraitError):
            reconstituted.validate(p, "married", "unknown")

    def test_pickle_shadow_trait(self):
        class Person(HasTraits):
            married = Map({"yes": 1, "yeah": 1, "no": 0, "nah": 0},
                          default_value="yes")

        p = Person()
        married_shadow_trait = p.trait("married_")
        reconstituted = pickle.loads(pickle.dumps(married_shadow_trait))

        default_value_callable = reconstituted.default_value()[1]

        self.assertEqual(default_value_callable(p), 1)
