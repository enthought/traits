# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.api import Any, HasTraits
from traits.has_traits import TraitsWarning


class TestTraitWarning(unittest.TestCase):

    def test_invalid_trait_name_prefix(self):
        with self.assertWarns(TraitsWarning):
            class UserDefinedClass(HasTraits):
                trait = "something"

        with self.assertWarns(TraitsWarning):
            class UserDefinedClass2(HasTraits):
                _trait = "something"

        with self.assertWarns(TraitsWarning):
            class UserDefinedClass3(HasTraits):
                _trait_suffix = "something"

        # Test invalid name using add_trait
        class UserDefinedClass4(HasTraits):
            valid_trait = Any()

        obj = UserDefinedClass4()
        with self.assertWarns(TraitsWarning):
            obj.add_trait("trait_invalid", Any())
        with self.assertWarns(TraitsWarning):
            obj.add_trait("_trait_invalid2", Any())
