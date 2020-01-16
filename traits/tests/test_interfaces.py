# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Unit test case for testing interfaces and adaptation.
"""

import unittest

from traits.api import (
    HasTraits,
    Adapter,
    AdaptsTo,
    Instance,
    Int,
    Interface,
    List,
    provides,
    register_factory,
    Supports,
    TraitError,
)
from traits.adaptation.api import reset_global_adaptation_manager


class IFoo(Interface):
    def get_foo(self):
        """ Returns the current foo. """


class IFooPlus(IFoo):
    def get_foo_plus(self):
        """ Returns even more foo. """


class IAverage(Interface):
    def get_average(self):
        """ Returns the average value for the object. """


class IList(Interface):
    def get_list(self):
        """ Returns the list value for the object. """


class Sample(HasTraits):

    s1 = Int(1, sample=True)
    s2 = Int(2, sample=True)
    s3 = Int(3, sample=True)
    i1 = Int(4)
    i2 = Int(5)
    i3 = Int(6)


@provides(IList)
class SampleList(HasTraits):
    """SampleList docstring."""

    data = List(Int, [10, 20, 30])

    def get_list(self):
        return self.data


@provides(IList, IAverage)
class SampleAverage(HasTraits):

    data = List(Int, [100, 200, 300])

    def get_list(self):
        return self.data

    def get_average(self):
        value = self.get_list()
        if len(value) == 0:
            return 0.0

        average = 0.0
        for item in value:
            average += item
        return average / len(value)


class UndeclaredAverageProvider(HasTraits):
    """
    Class that conforms to the IAverage interface, but doesn't declare
    that it does so.
    """
    def get_average(self):
        return 5.6


class SampleBad(HasTraits):
    pass


class TraitsHolder(HasTraits):

    a_no = Instance(IAverage, adapt="no")
    a_yes = Instance(IAverage, adapt="yes")
    a_default = Instance(IAverage, adapt="default")
    list_adapted_to = Supports(IList)
    foo_adapted_to = Supports(IFoo)
    foo_plus_adapted_to = Supports(IFooPlus)
    list_adapts_to = AdaptsTo(IList)
    foo_adapts_to = AdaptsTo(IFoo)
    foo_plus_adapts_to = AdaptsTo(IFooPlus)


class SampleListAdapter(Adapter):
    def get_list(self):
        obj = self.adaptee
        return [getattr(obj, name) for name in obj.trait_names(sample=True)]


class ListAverageAdapter(Adapter):
    def get_average(self):
        value = self.adaptee.get_list()
        if len(value) == 0:
            return 0.0

        average = 0.0
        for item in value:
            average += item
        return average / len(value)


class SampleFooAdapter(HasTraits):

    object = Instance(Sample)

    def __init__(self, object):
        self.object = object

    def get_foo(self):
        object = self.object
        return object.s1 + object.s2 + object.s3


class FooPlusAdapter(object):
    def __init__(self, obj):
        self.obj = obj

    def get_foo(self):
        return self.obj.get_foo()

    def get_foo_plus(self):
        return self.obj.get_foo() + 1


class InterfacesTest(unittest.TestCase):

    #### 'TestCase' protocol ##################################################

    def setUp(self):
        reset_global_adaptation_manager()

        # Register adapters.
        register_factory(SampleListAdapter, Sample, IList)
        register_factory(ListAverageAdapter, IList, IAverage)
        register_factory(SampleFooAdapter, Sample, IFoo)
        register_factory(FooPlusAdapter, IFoo, IFooPlus)

    #### Tests ################################################################

    def test_provides_none(self):
        @provides()
        class Test(HasTraits):
            pass

    def test_provides_one(self):
        @provides(IFoo)
        class Test(HasTraits):
            pass

    def test_provides_multi(self):
        @provides(IFoo, IAverage, IList)
        class Test(HasTraits):
            pass

    def test_provides_extended(self):
        """ Ensure that subclasses of Interfaces imply the superinterface.
        """

        @provides(IFooPlus)
        class Test(HasTraits):
            pass

        ta = TraitsHolder()
        ta.foo_adapted_to = Test()

    def test_provides_bad(self):
        with self.assertRaises(Exception):

            @provides(Sample)
            class Test(HasTraits):
                pass

    def test_instance_adapt_no(self):
        ta = TraitsHolder()

        # Verify that SampleAverage() does not raise an error (it is an
        # instance of the IAverage interface).
        try:
            ta.a_no = SampleAverage()
        except TraitError:
            self.fail(
                "Setting instance of interface should not require "
                "adaptation"
            )

        # These are not instances of the IAverage interface, and therefore
        # cannot be set to the trait.
        self.assertRaises(TraitError, ta.trait_set, a_no=SampleList())
        self.assertRaises(TraitError, ta.trait_set, a_no=Sample())
        self.assertRaises(TraitError, ta.trait_set, a_no=SampleBad())

    def test_instance_adapt_yes(self):
        ta = TraitsHolder()

        ta.a_yes = SampleAverage()
        self.assertEqual(ta.a_yes.get_average(), 200.0)
        self.assertIsInstance(ta.a_yes, SampleAverage)
        self.assertFalse(hasattr(ta, "a_yes_"))

        ta.a_yes = SampleList()
        self.assertEqual(ta.a_yes.get_average(), 20.0)
        self.assertIsInstance(ta.a_yes, ListAverageAdapter)
        self.assertFalse(hasattr(ta, "a_yes_"))

        ta.a_yes = Sample()
        self.assertEqual(ta.a_yes.get_average(), 2.0)
        self.assertIsInstance(ta.a_yes, ListAverageAdapter)
        self.assertFalse(hasattr(ta, "a_yes_"))

        self.assertRaises(TraitError, ta.trait_set, a_yes=SampleBad())

    def test_instance_adapt_default(self):
        ta = TraitsHolder()

        ta.a_default = SampleAverage()
        self.assertEqual(ta.a_default.get_average(), 200.0)
        self.assertIsInstance(ta.a_default, SampleAverage)
        self.assertFalse(hasattr(ta, "a_default_"))

        ta.a_default = SampleList()
        self.assertEqual(ta.a_default.get_average(), 20.0)
        self.assertIsInstance(ta.a_default, ListAverageAdapter)
        self.assertFalse(hasattr(ta, "a_default_"))

        ta.a_default = Sample()
        self.assertEqual(ta.a_default.get_average(), 2.0)
        self.assertIsInstance(ta.a_default, ListAverageAdapter)
        self.assertFalse(hasattr(ta, "a_default_"))

        ta.a_default = SampleBad()
        self.assertEqual(ta.a_default, None)
        self.assertFalse(hasattr(ta, "a_default_"))

    def test_adapted_to(self):
        ta = TraitsHolder()

        ta.list_adapted_to = object = Sample()
        result = ta.list_adapted_to.get_list()
        self.assertEqual(len(result), 3)
        for n in [1, 2, 3]:
            self.assertIn(n, result)
        self.assertIsInstance(ta.list_adapted_to, SampleListAdapter)
        self.assertEqual(ta.list_adapted_to_, object)

        ta.foo_adapted_to = object = Sample()
        self.assertEqual(ta.foo_adapted_to.get_foo(), 6)
        self.assertIsInstance(ta.foo_adapted_to, SampleFooAdapter)
        self.assertEqual(ta.foo_adapted_to_, object)

        ta.foo_plus_adapted_to = object = Sample(s1=5, s2=10, s3=15)
        self.assertEqual(ta.foo_plus_adapted_to.get_foo(), 30)
        self.assertEqual(ta.foo_plus_adapted_to.get_foo_plus(), 31)
        self.assertIsInstance(ta.foo_plus_adapted_to, FooPlusAdapter)
        self.assertEqual(ta.foo_plus_adapted_to_, object)

    def test_adapts_to(self):
        ta = TraitsHolder()

        ta.list_adapts_to = object = Sample()
        self.assertEqual(ta.list_adapts_to, object)
        result = ta.list_adapts_to_.get_list()
        self.assertEqual(len(result), 3)
        for n in [1, 2, 3]:
            self.assertIn(n, result)
        self.assertIsInstance(ta.list_adapts_to_, SampleListAdapter)

        ta.foo_adapts_to = object = Sample()
        self.assertEqual(ta.foo_adapts_to, object)
        self.assertEqual(ta.foo_adapts_to_.get_foo(), 6)
        self.assertIsInstance(ta.foo_adapts_to_, SampleFooAdapter)

        ta.foo_plus_adapts_to = object = Sample(s1=5, s2=10, s3=15)
        self.assertEqual(ta.foo_plus_adapts_to, object)
        self.assertEqual(ta.foo_plus_adapts_to_.get_foo(), 30)
        self.assertEqual(ta.foo_plus_adapts_to_.get_foo_plus(), 31)
        self.assertIsInstance(ta.foo_plus_adapts_to_, FooPlusAdapter)

    def test_decorated_class_name_and_docstring(self):
        self.assertEqual(SampleList.__name__, "SampleList")
        self.assertEqual(SampleList.__doc__, "SampleList docstring.")

    def test_instance_requires_provides(self):
        ta = TraitsHolder()
        provider = UndeclaredAverageProvider()
        with self.assertRaises(TraitError):
            ta.a_no = provider
