# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.adaptation.api import reset_global_adaptation_manager
from traits.api import (
    BaseInstance,
    Bool,
    HasTraits,
    Instance,
    List,
    register_factory,
    TraitError,
)


class Foo(HasTraits):
    default = Bool(False)


class Bar(HasTraits):
    pass


def bar_to_foo_adapter(bar):
    return Foo()


def default_foo():
    return Foo(default=True)


class AutomaticAdaptationTestMixin:
    """
    Mixin for tests to be applied to both Instance and BaseInstance.

    Subclasses should define the class variable 'trait_under_test'.
    """

    #### 'TestCase' protocol ##################################################

    def setUp(self):
        reset_global_adaptation_manager()

    #### Tests ################################################################

    def test_instance_trait_automatic_adaptation(self):
        bar = Bar()
        foo_container = self.create_foo_container()

        # Before a Bar->Foo adapter is registered.
        with self.assertRaises(TraitError):
            foo_container.not_adapting_foo = bar

        with self.assertRaises(TraitError):
            foo_container.adapting_foo = bar

        foo_container.adapting_foo_permissive = bar
        self.assertIsNone(foo_container.adapting_foo_permissive)

        foo_container.adapting_foo_dynamic_default = bar
        self.assertIsInstance(foo_container.adapting_foo_dynamic_default, Foo)
        self.assertTrue(foo_container.adapting_foo_dynamic_default.default)

        # After a Bar->Foo adapter is registered.
        register_factory(bar_to_foo_adapter, Bar, Foo)

        with self.assertRaises(TraitError):
            foo_container.not_adapting_foo = bar

        foo_container.adapting_foo = bar
        self.assertIsInstance(foo_container.adapting_foo, Foo)

        foo_container.adapting_foo_permissive = bar
        self.assertIsInstance(foo_container.adapting_foo_permissive, Foo)

        foo_container.adapting_foo_dynamic_default = bar
        self.assertIsInstance(foo_container.adapting_foo_dynamic_default, Foo)
        self.assertFalse(foo_container.adapting_foo_dynamic_default.default)

    def test_list_trait_automatic_adaptation(self):
        bar = Bar()
        foo_container = self.create_foo_container()

        # Before a Bar->Foo adapter is registered.
        with self.assertRaises(TraitError):
            foo_container.not_adapting_foo_list = [bar]

        with self.assertRaises(TraitError):
            foo_container.adapting_foo_list = [bar]

        # After a Bar->Foo adapter is registered.
        register_factory(bar_to_foo_adapter, Bar, Foo)

        with self.assertRaises(TraitError):
            foo_container.not_adapting_foo_list = [bar]

        foo_container.adapting_foo_list = [bar]
        self.assertIsInstance(foo_container.adapting_foo_list[0], Foo)

    #### Helpers ##############################################################

    def create_foo_container(self):

        instance_trait = self.trait_under_test

        class FooContainer(HasTraits):
            not_adapting_foo = instance_trait(Foo)
            adapting_foo = instance_trait(Foo, adapt="yes")
            adapting_foo_permissive = instance_trait(Foo, adapt="default")
            adapting_foo_dynamic_default = instance_trait(
                Foo,
                adapt="default",
                factory=default_foo,
            )
            not_adapting_foo_list = List(Foo)
            adapting_foo_list = List(instance_trait(Foo, adapt="yes"))

        return FooContainer()


class TestAutomaticAdaptationInstance(
    AutomaticAdaptationTestMixin, unittest.TestCase
):
    """
    Tests for automatic adaptation with Instance.
    """

    #: Trait type being tested
    trait_under_test = Instance


class TestAutomaticAdaptationBaseInstance(
    AutomaticAdaptationTestMixin, unittest.TestCase
):
    """
    Tests for automatic adaptation with BaseInstance.
    """

    #: Trait type being tested
    trait_under_test = BaseInstance
