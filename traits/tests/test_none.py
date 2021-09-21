# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.api import HasTraits, TraitError
from traits.trait_types import _NoneTrait


class A(HasTraits):
    none_atr = _NoneTrait(default_value=None)


class TestCaseNoneTrait(unittest.TestCase):
    def test_none(self):
        obj = A()
        self.assertIsNone(obj.none_atr)

    def test_assign_non_none(self):
        with self.assertRaises(TraitError):
            A(none_atr=5)

    def test_default_value_not_none(self):
        with self.assertRaises(ValueError):
            class TestClass(HasTraits):
                none_trait = _NoneTrait(default_value=[])
