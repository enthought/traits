# ------------------------------------------------------------------------------
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
# ------------------------------------------------------------------------------"""

"""
Tests for the Type trait type.
"""

from __future__ import absolute_import, print_function, unicode_literals

import pickle
import unittest

from traits.api import HasTraits, Type


class HasTypeTrait(HasTraits):
    foo = Type(klass=Exception, value="traits.api.TraitError")


class TestType(unittest.TestCase):
    def test_pickleable(self):
        has_type_trait = HasTypeTrait()

        # Adding a listener has the side-effect of creating an entry in
        # has_type_traits.__instance_traits__, which then also needs to be
        # pickleable. Ref: enthought/traits#452.
        has_type_trait.on_trait_change(lambda: None, "foo")

        pickled = pickle.dumps(has_type_trait)
        unpickled = pickle.loads(pickled)
        self.assertIsInstance(unpickled, HasTypeTrait)
