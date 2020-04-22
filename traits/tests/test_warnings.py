# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from unittest import mock, TestCase

from traits.api import Any, HasTraits


def mock_module_name(name):
    return mock.patch(__name__ + ".__name__", name)


class TestTraitWarning(TestCase):

    def test_invalid_trait_name_prefix(self):
        with mock_module_name("usermodule"):
            with self.assertWarns(UserWarning):
                class UserDefinedClass(HasTraits):
                    trait = "something"
                UserDefinedClass()

            with self.assertWarns(UserWarning):
                class UserDefinedClass2(HasTraits):
                    _trait = "something"

                UserDefinedClass2()

            with self.assertWarns(UserWarning):
                class UserDefinedClass3(HasTraits):
                    _trait_suffix = "something"

                UserDefinedClass3()

            # Test invalid name using add_trait
            class UserDefinedClass4(HasTraits):
                valid_trait = Any()

            obj = UserDefinedClass4()
            with self.assertWarns(UserWarning):
                obj.add_trait("trait_invalid", Any())
            with self.assertWarns(UserWarning):
                obj.add_trait("_trait_invalid2", Any())
