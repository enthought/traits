""" Test the adapter registry. """


import unittest

from apptools.adaptation.adapter_registry import AdapterRegistry


class TestAdapterRegistry(unittest.TestCase):
    """ Test the adapter registry. """

    #### 'TestCase' protocol ##################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        self.adapter_registry = AdapterRegistry()

        return

    def tearDown(self):
        """ Called immediately after each test method has been called. """

        return

    #### Tests ################################################################

    def test_no_adapter_required_with_abcs(self):

        from apptools.adaptation.tests.abc_examples import Foo, FooABC

        f = Foo()

        # Try to adapt it to its own concrete type.
        foo = self.adapter_registry.adapt(f, Foo)

        # The adapter  manager should simply return the same object.
        self.assert_(foo is f)

        # Try to adapt it to an ABC that is registered for its type.
        foo = self.adapter_registry.adapt(f, FooABC)

        # The adapter  manager should simply return the same object.
        self.assert_(foo is f)

        return

    def test_no_adapter_required_with_interfaces(self):

        from apptools.adaptation.tests.interface_examples import Foo, IFoo

        f = Foo()

        # Try to adapt it to its own concrete type.
        foo = self.adapter_registry.adapt(f, Foo)

        # The adapter  manager should simply return the same object.
        self.assert_(foo is f)

        # Try to adapt it to an ABC that is registered for its type.
        foo = self.adapter_registry.adapt(f, IFoo)

        # The adapter  manager should simply return the same object.
        self.assert_(foo is f)

        return

    def test_no_adapter_available_with_abcs(self):

        from apptools.adaptation.tests.abc_examples import (
            Bar, BarABC, Foo
        )

        f = Foo()

        # Try to adapt it to a concrete type.
        bar = self.adapter_registry.adapt(f, Bar)

        # There should be no way to adapt a Foo to a Bar.
        self.assertEqual(bar, None)

        # Try to adapt it to an ABC.
        bar = self.adapter_registry.adapt(f, BarABC)

        # There should be no way to adapt a Foo to a Bar.
        self.assertEqual(bar, None)

        return

    def test_no_adapter_available_with_interfaces(self):

        from apptools.adaptation.tests.interface_examples import (
            Bar, IBar, Foo
        )

        f = Foo()

        # Try to adapt it to a concrete type.
        bar = self.adapter_registry.adapt(f, Bar)

        # There should be no way to adapt a Foo to a Bar.
        self.assertEqual(bar, None)

        # Try to adapt it to an Interface.
        bar = self.adapter_registry.adapt(f, IBar)

        # There should be no way to adapt a Foo to a Bar.
        self.assertEqual(bar, None)

        return

    def test_one_step_adaptation_with_abcs(self):

        from apptools.adaptation.adapter_factory import AdapterFactory

        from apptools.adaptation.tests.abc_examples import (
            FooABCToBarABCAdapter,
            FooABC,
            BarABC,
            Foo,
            Bar
        )

        # FooABC->BarABC.
        self.adapter_registry.register_adapter_factory(
            AdapterFactory(
                factory       = FooABCToBarABCAdapter,
                from_protocol = FooABC,
                to_protocol   = BarABC
            )
        )

        f = Foo()

        # Adapt it to an ABC.
        bar = self.adapter_registry.adapt(f, BarABC)
        self.assertIsNotNone(bar)
        self.assertIsInstance(bar, FooABCToBarABCAdapter)

        # We shouldn't be able to adapt it to a *concrete* 'Bar' though.
        bar = self.adapter_registry.adapt(f, Bar)
        self.assertIsNone(bar)

        return

    def test_one_step_adaptation_with_interfaces(self):

        from apptools.adaptation.adapter_factory import AdapterFactory

        from apptools.adaptation.tests.interface_examples import (
            IFooToIBarAdapter,
            IFoo,
            IBar,
            Foo,
            Bar
        )

        # FooABC->BarABC.
        self.adapter_registry.register_adapter_factory(
            AdapterFactory(
                factory       = IFooToIBarAdapter,
                from_protocol = IFoo,
                to_protocol   = IBar
            )
        )

        f = Foo()

        # Adapt it to an ABC.
        bar = self.adapter_registry.adapt(f, IBar)
        self.assertIsNotNone(bar)
        self.assertIsInstance(bar, IFooToIBarAdapter)

        # We shouldn't be able to adapt it to a *concrete* 'Bar' though.
        bar = self.adapter_registry.adapt(f, Bar)
        self.assertIsNone(bar)

        return

    def test_adapter_chaining_with_abcs(self):

        from apptools.adaptation.adapter_factory import AdapterFactory

        from apptools.adaptation.tests.abc_examples import (
            FooABCToBarABCAdapter,
            BarABCToBazABCAdapter,
            FooABC,
            BarABC,
            BazABC,
            Foo
        )

        # FooABC->BarABC.
        self.adapter_registry.register_adapter_factory(
            AdapterFactory(
                factory       = FooABCToBarABCAdapter,
                from_protocol = FooABC,
                to_protocol   = BarABC
            )
        )

        # BarABC->BazABC.
        self.adapter_registry.register_adapter_factory(
            AdapterFactory(
                factory       = BarABCToBazABCAdapter,
                from_protocol = BarABC,
                to_protocol   = BazABC
            )
        )

        # Create a Foo.
        foo = Foo()

        # Adapt it to a BazABC via the chain.
        baz = self.adapter_registry.adapt(foo, BazABC)
        self.assertIsNotNone(baz)
        self.assertIsInstance(baz, BarABCToBazABCAdapter)
        self.assert_(baz.adaptee.adaptee is foo)
        
        return

    def test_adapter_chaining_with_interfaces(self):

        from apptools.adaptation.adapter_factory import AdapterFactory

        from apptools.adaptation.tests.interface_examples import (
            IFooToIBarAdapter,
            IBarToIBazAdapter,
            IFoo,
            IBar,
            IBaz,
            Foo
        )

        # IFoo->IBar.
        self.adapter_registry.register_adapter_factory(
            AdapterFactory(
                factory       = IFooToIBarAdapter,
                from_protocol = IFoo,
                to_protocol   = IBar
            )
        )

        # IBar->IBaz.
        self.adapter_registry.register_adapter_factory(
            AdapterFactory(
                factory       = IBarToIBazAdapter,
                from_protocol = IBar,
                to_protocol   = IBaz
            )
        )

        # Create a Foo.
        foo = Foo()

        # Adapt it to an IBaz via the chain.
        baz = self.adapter_registry.adapt(foo, IBaz)
        self.assertIsNotNone(baz)
        self.assertIsInstance(baz, IBarToIBazAdapter)
        self.assert_(baz.adaptee.adaptee is foo)
        
        return

#### EOF ######################################################################
