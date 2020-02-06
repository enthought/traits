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
Tests for the PrefixMap handler.
"""

import pickle
import unittest

from traits.api import HasTraits, TraitError, PrefixMap


class TestPrefixMap(unittest.TestCase):
    def test_assignment(self):
        class Person(HasTraits):
            married = PrefixMap({"yes": 1, "yeah": 1, "no": 0, "nah": 0})

        person = Person()

        self.assertIsNone(person.married)

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

    def test_invalid_default(self):
        with self.assertRaises(ValueError):
            class Person(HasTraits):
                married = PrefixMap({"yes": 1, "yeah": 1, "no": 0, "nah": 0},
                                    default_value="ye")

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
            self.assertEqual(reconstituted.validate(p, "married", "uknown"),
                             "unknown")

        with self.assertRaises(TraitError):
            self.assertEqual(reconstituted.validate(p, "married", "ye"),
                             "yeah")
