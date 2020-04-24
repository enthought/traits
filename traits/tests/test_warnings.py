# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
import contextlib

from unittest import mock, TestCase

from traits.api import Any, HasTraits
from traits.has_traits import AbstractViewElement


def mock_module_name(name):
    return mock.patch(__name__ + ".__name__", name)


class DummyViewElement(AbstractViewElement):
    """ Dummy view for testing purposes."""
    pass


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

    def test_traits_view_whitelisted(self):
        with mock_module_name("usermodule"):
            with self._assert_no_warnings(UserWarning):
                class UserDefinedClass(HasTraits):
                    traits_view = DummyViewElement()

    def test_traits_init_whitelisted(self):
        with mock_module_name("usermodule"):
            with self._assert_no_warnings(UserWarning):
                class UserDefinedClass(HasTraits):

                    def traits_init(self):
                        pass

    def test_trait_context_whitelisted(self):
        with mock_module_name("usermodule"):
            with self._assert_no_warnings(UserWarning):
                class UserDefinedClass(HasTraits):

                    def trait_context(self):
                        return {}

    @contextlib.contextmanager
    def _assert_no_warnings(self, category):
        # There may be an assertNoWarns from unittest in the future
        # see https://bugs.python.org/issue39385
        try:
            with self.assertWarns(category) as cm:
                yield
        except AssertionError:
            # This may silence other, unexpected assertion errors.
            pass
        else:
            self.fail("Expected no warnings, got {!r}".format(cm.warning))
