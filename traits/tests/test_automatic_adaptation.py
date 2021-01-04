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

from traits.adaptation.api import reset_global_adaptation_manager
from traits.api import HasTraits, Instance, List, register_factory, TraitError


class Foo(HasTraits):
    pass


class Bar(HasTraits):
    pass


def bar_to_foo_adapter(bar):
    return Foo()


class FooContainer(HasTraits):
    not_adapting_foo = Instance(Foo)
    adapting_foo = Instance(Foo, adapt="yes")

    not_adapting_foo_list = List(Foo)
    adapting_foo_list = List(Instance(Foo, adapt="yes"))


class TestAutomaticAdaptation(unittest.TestCase):

    #### 'TestCase' protocol ##################################################

    def setUp(self):
        reset_global_adaptation_manager()

    #### Tests ################################################################

    def test_instance_trait_automatic_adaptation(self):
        bar = Bar()
        foo_container = FooContainer()

        # Before a Bar->Foo adapter is registered.
        with self.assertRaises(TraitError):
            foo_container.not_adapting_foo = bar

        with self.assertRaises(TraitError):
            foo_container.adapting_foo = bar

        # After a Bar->Foo adapter is registered.
        register_factory(bar_to_foo_adapter, Bar, Foo)

        with self.assertRaises(TraitError):
            foo_container.not_adapting_foo = bar

        foo_container.adapting_foo = bar
        self.assertIsInstance(foo_container.adapting_foo, Foo)

    def test_list_trait_automatic_adaptation(self):
        bar = Bar()
        foo_container = FooContainer()

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
