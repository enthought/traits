#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt

""" Tests to help find out if we can do type-safe casting. """

from __future__ import absolute_import

# Standard library imports.
import unittest
import warnings

# Enthought library imports.
from traits.adaptation.api import reset_global_adaptation_manager
from traits.api import (
    Adapter,
    HasTraits,
    Instance,
    Int,
    Interface,
    provides,
    register_factory,
)

# Local imports.
from traits.interface_checker import InterfaceError, check_implements

# Make sure implicit interface checking is turned off, so that we can make the
# checks explicitly:
from traits import has_traits

has_traits.CHECK_INTERFACES = 0


class InterfaceCheckerTestCase(unittest.TestCase):
    """ Tests to help find out if we can do type-safe casting. """

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """
        reset_global_adaptation_manager()

        return

    ###########################################################################
    # Tests.
    ###########################################################################

    def test_non_traits_class(self):
        """ non-traits class """

        class IFoo(Interface):
            def foo(self):
                pass

        # A class that *does* implement the interface.
        @provides(IFoo)
        class Foo(object):
            def foo(self):
                pass

        # The checker will raise an exception if the class does not implement
        # the interface.
        check_implements(Foo, IFoo, 2)

        return

    def test_single_interface(self):
        """ single interface """

        class IFoo(Interface):
            x = Int

        # A class that *does* implement the interface.
        @provides(IFoo)
        class Foo(HasTraits):

            x = Int

        # The checker will raise an exception if the class does not implement
        # the interface.
        check_implements(Foo, IFoo, 2)

        return

    def test_single_interface_with_invalid_method_signature(self):
        """ single interface with invalid method signature """

        class IFoo(Interface):
            def foo(self):
                pass

        # A class that does *not* implement the interface.
        @provides(IFoo)
        class Foo(HasTraits):
            # Extra argument!
            def foo(self, x):
                pass

        self.assertRaises(InterfaceError, check_implements, Foo, IFoo, 2)

        return

    def test_single_interface_with_missing_trait(self):
        """ single interface with missing trait """

        class IFoo(Interface):
            x = Int

        # A class that does *not* implement the interface.
        @provides(IFoo)
        class Foo(HasTraits):
            pass

        self.assertRaises(InterfaceError, check_implements, Foo, IFoo, 2)
        return

    def test_single_interface_with_missing_method(self):
        """ single interface with missing method """

        class IFoo(Interface):
            def method(self):
                pass

        # A class that does *not* implement the interface.
        @provides(IFoo)
        class Foo(HasTraits):
            pass

        self.assertRaises(InterfaceError, check_implements, Foo, IFoo, 2)

        return

    def test_multiple_interfaces(self):
        """ multiple interfaces """

        class IFoo(Interface):
            x = Int

        class IBar(Interface):
            y = Int

        class IBaz(Interface):
            z = Int

        # A class that *does* implement the interface.
        @provides(IFoo, IBar, IBaz)
        class Foo(HasTraits):
            x = Int
            y = Int
            z = Int

        # The checker will raise an exception if the class does not implement
        # the interface.
        check_implements(Foo, [IFoo, IBar, IBaz], 2)

        return

    def test_multiple_interfaces_with_invalid_method_signature(self):
        """ multiple interfaces with invalid method signature """

        class IFoo(Interface):
            def foo(self):
                pass

        class IBar(Interface):
            def bar(self):
                pass

        class IBaz(Interface):
            def baz(self):
                pass

        # A class that does *not* implement the interface.
        @provides(IFoo, IBar, IBaz)
        class Foo(HasTraits):
            def foo(self):
                pass

            def bar(self):
                pass

            # Extra argument!
            def baz(self, x):
                pass

        self.assertRaises(
            InterfaceError, check_implements, Foo, [IFoo, IBar, IBaz], 2
        )

        return

    def test_multiple_interfaces_with_missing_trait(self):
        """ multiple interfaces with missing trait """

        class IFoo(Interface):
            x = Int

        class IBar(Interface):
            y = Int

        class IBaz(Interface):
            z = Int

        # A class that does *not* implement the interface.
        @provides(IFoo, IBar, IBaz)
        class Foo(HasTraits):

            x = Int
            y = Int

        self.assertRaises(
            InterfaceError, check_implements, Foo, [IFoo, IBar, IBaz], 2
        )

        return

    def test_multiple_interfaces_with_missing_method(self):
        """ multiple interfaces with missing method """

        class IFoo(Interface):
            def foo(self):
                pass

        class IBar(Interface):
            def bar(self):
                pass

        class IBaz(Interface):
            def baz(self):
                pass

        # A class that does *not* implement the interface.
        @provides(IFoo, IBar, IBaz)
        class Foo(HasTraits):
            def foo(self):
                pass

            def bar(self):
                pass

        self.assertRaises(
            InterfaceError, check_implements, Foo, [IFoo, IBar, IBaz], 2
        )

        return

    def test_inherited_interfaces(self):
        """ inherited interfaces """

        class IFoo(Interface):
            x = Int

        class IBar(IFoo):
            y = Int

        class IBaz(IBar):
            z = Int

        # A class that *does* implement the interface.
        @provides(IBaz)
        class Foo(HasTraits):
            x = Int
            y = Int
            z = Int

        # The checker will raise an exception if the class does not implement
        # the interface.
        check_implements(Foo, IBaz, 2)

        return

    def test_inherited_interfaces_with_invalid_method_signature(self):
        """ inherited with invalid method signature """

        class IFoo(Interface):
            def foo(self):
                pass

        class IBar(IFoo):
            def bar(self):
                pass

        class IBaz(IBar):
            def baz(self):
                pass

        # A class that does *not* implement the interface.
        @provides(IBaz)
        class Foo(HasTraits):
            def foo(self):
                pass

            def bar(self):
                pass

            # Extra argument!
            def baz(self, x):
                pass

        self.assertRaises(InterfaceError, check_implements, Foo, IBaz, 2)

        return

    def test_inherited_interfaces_with_missing_trait(self):
        """ inherited interfaces with missing trait """

        class IFoo(Interface):
            x = Int

        class IBar(IFoo):
            y = Int

        class IBaz(IBar):
            z = Int

        # A class that does *not* implement the interface.
        @provides(IBaz)
        class Foo(HasTraits):

            x = Int
            y = Int

        self.assertRaises(InterfaceError, check_implements, Foo, IBaz, 2)

        return

    def test_inherited_interfaces_with_missing_method(self):
        """ inherited interfaces with missing method """

        class IFoo(Interface):
            def foo(self):
                pass

        class IBar(IFoo):
            def bar(self):
                pass

        class IBaz(IBar):
            def baz(self):
                pass

        # A class that does *not* implement the interface.
        @provides(IBaz)
        class Foo(HasTraits):
            def foo(self):
                pass

            def bar(self):
                pass

        self.assertRaises(InterfaceError, check_implements, Foo, IBaz, 2)

        return

    def test_subclasses_with_wrong_signature_methods(self):
        """ Subclasses with incorrect method signatures """

        class IFoo(Interface):
            def foo(self, argument):
                pass

        @provides(IFoo)
        class Foo(HasTraits):
            def foo(self, argument):
                pass

        class Bar(Foo):
            def foo(self):
                pass

        self.assertRaises(InterfaceError, check_implements, Bar, IFoo, 2)

    # Make sure interfaces and adaptation etc still work with the 'HasTraits'
    # version of 'Interface'!
    def test_instance(self):
        """ instance """

        class IFoo(Interface):
            pass

        @provides(IFoo)
        class Foo(HasTraits):
            pass

        class Bar(HasTraits):
            foo = Instance(IFoo)

        Bar(foo=Foo())

        return

    def test_callable(self):
        """ callable """

        class IFoo(Interface):
            pass

        @provides(IFoo)
        class Foo(HasTraits):
            pass

        f = Foo()

        # Adaptation via direct instantiation of interfaces is deprecated, so
        # catch the warning to keep the test run output clean.
        with warnings.catch_warnings(record=True) as warn_msgs:
            warnings.simplefilter("always", DeprecationWarning)
            self.assertEqual(f, IFoo(f))

        self.assertEqual(len(warn_msgs), 1)
        warn_msg = warn_msgs[0]
        self.assertIn(
            'use "adapt(adaptee, protocol)" instead', str(warn_msg.message))
        self.assertIn("test_interface_checker", warn_msg.filename)

    def test_adaptation(self):
        """ adaptation """

        class IFoo(Interface):
            pass

        class Foo(HasTraits):
            pass

        @provides(IFoo)
        class FooToIFooAdapter(Adapter):
            pass

        register_factory(FooToIFooAdapter, Foo, IFoo)

        f = Foo()

        # Make sure adaptation works. Adaptation via direct instantiation of
        # Interface classes is deprecated, so suppress the warning.
        with warnings.catch_warnings(record=True) as warn_msgs:
            warnings.simplefilter("always", DeprecationWarning)
            i_foo = IFoo(f)

        self.assertNotEqual(None, i_foo)
        self.assertEqual(FooToIFooAdapter, type(i_foo))

        self.assertEqual(len(warn_msgs), 1)
        warn_msg = warn_msgs[0]
        self.assertIn(
            'use "adapt(adaptee, protocol)" instead', str(warn_msg.message))
        self.assertIn("test_interface_checker", warn_msg.filename)
