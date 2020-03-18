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
import unittest

from traits.api import HasTraits, TraitError, Map, Undefined


class TestMap(unittest.TestCase):
    def test_assignment(self):
        class Person(HasTraits):
            married = Map({"yes": 1, "yeah": 1, "no": 0, "nah": 0})

        person = Person()

        self.assertEqual(Undefined, person.married)

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

    def test_default(self):
        class Person(HasTraits):
            married = Map({"yes": 1, "yeah": 1, "no": 0, "nah": 0,
                           None: 2}, default_value=None)

        p = Person()
        self.assertIsNone(p.married)
        self.assertEqual(p.married_, 2)

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
            self.assertEqual(reconstituted.validate(p, "married", "uknown"),
                             "unknown")
