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
Tests for the Instance trait type.
"""

from __future__ import absolute_import, print_function, unicode_literals

import pickle
import unittest

from traits.api import HasTraits, Instance


class HasInstance(HasTraits):
    my_slice = Instance(slice, (0, 10))


class TestInstance(unittest.TestCase):
    def test_pickleable(self):
        has_instance = HasInstance(my_slice=slice(2, 5))

        pickled = pickle.dumps(has_instance)
        unpickled = pickle.loads(pickled)
        self.assertIsInstance(unpickled, HasInstance)
        self.assertEqual(unpickled.my_slice, slice(2, 5))

        # Adding a listener has the side-effect of creating an entry in
        # has_instance.__instance_traits__, which then also needs to be
        # pickleable. Ref: enthought/traits#452.
        has_instance.on_trait_change(lambda: None, "my_slice")
        pickled = pickle.dumps(has_instance)
        unpickled = pickle.loads(pickled)
        self.assertIsInstance(unpickled, HasInstance)
        self.assertEqual(unpickled.my_slice, slice(2, 5))

    def test_added_trait_pickleable(self):
        has_instance = HasInstance(my_slice=slice(2, 5))
        has_instance.add_trait("my_other_slice", Instance(slice, (20, 30)))

        pickled = pickle.dumps(has_instance)
        unpickled = pickle.loads(pickled)
        self.assertIsInstance(unpickled, HasInstance)
        self.assertEqual(unpickled.my_slice, slice(2, 5))
        self.assertEqual(unpickled.my_other_slice, slice(20, 30))
