# -----------------------------------------------------------------------------
#
#  Copyright (c) 2019, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
# -----------------------------------------------------------------------------

"""
Tests for the UUID trait type.
"""
from __future__ import absolute_import, print_function, unicode_literals

import pickle
import unittest
import uuid

from traits.api import CTrait, HasTraits, TraitError, UUID


class HasUUIDTrait(HasTraits):
    foo_id = UUID()


class TestUUID(unittest.TestCase):
    def test_get(self):
        has_uuid = HasUUIDTrait()
        id1 = has_uuid.foo_id
        self.assertIsInstance(id1, uuid.UUID)
        id2 = has_uuid.foo_id
        self.assertEqual(id1, id2)

    def test_set(self):
        has_uuid = HasUUIDTrait()
        # UUID traits are read-only.
        with self.assertRaises(TraitError):
            has_uuid.foo_id = uuid.uuid4()

    def test_pickleable(self):
        has_uuid = HasUUIDTrait()

        # Check that the trait itself can be pickled and unpickled.
        uuid_trait = has_uuid.traits()['foo_id']
        self.assertIsInstance(uuid_trait, CTrait)
        pickled = pickle.dumps(uuid_trait)
        unpickled = pickle.loads(pickled)

        self.assertIsInstance(unpickled.trait_type, UUID)
