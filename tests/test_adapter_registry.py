""" Test the adapter registry. """


import unittest

from apptools.adaptation.adapter_registry import AdapterRegistry
import apptools.adaptation.tests.abc_examples
import apptools.adaptation.tests.interface_examples


class _TestAdapterRegistry(unittest.TestCase):
    """ Test the adapter registry. """

    #: Class attribute pointing at the module containing the example data
    examples = None

    #### 'TestCase' protocol ##################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        self.adapter_registry = AdapterRegistry()

        return

    def tearDown(self):
        """ Called immediately after each test method has been called. """

        return

    #### Tests ################################################################

    def test_no_adapter_required(self):

        ex = self.examples

        plug = ex.UKPlug()

        # Try to adapt it to its own concrete type.
        uk_plug = self.adapter_registry.adapt(plug, ex.UKPlug)

        # The adapter registry should simply return the same object.
        self.assert_(uk_plug is plug)

        # Try to adapt it to an ABC that is registered for its type.
        uk_plug = self.adapter_registry.adapt(plug, ex.UKStandard)

        # The adapter registry should simply return the same object.
        self.assert_(uk_plug is plug)

        return

    def test_no_adapter_available(self):

        ex = self.examples

        plug = ex.UKPlug()

        # Try to adapt it to a concrete type.
        eu_plug = self.adapter_registry.adapt(plug, ex.EUPlug)

        # There should be no way to adapt a UKPlug to a EUPlug.
        self.assertEqual(eu_plug, None)

        # Try to adapt it to an ABC.
        eu_plug = self.adapter_registry.adapt(plug, ex.EUStandard)

        # There should be no way to adapt a UKPlug to a EUPlug.
        self.assertEqual(eu_plug, None)

        return

    def test_one_step_adaptation(self):

        from apptools.adaptation.adapter_factory import AdapterFactory

        ex = self.examples

        # UKStandard->EUStandard.
        self.adapter_registry.register_adapter_factory(
            AdapterFactory(
                factory       = ex.UKStandardToEUStandard,
                from_protocol = ex.UKStandard,
                to_protocol   = ex.EUStandard
            )
        )

        plug = ex.UKPlug()

        # Adapt it to an ABC.
        eu_plug = self.adapter_registry.adapt(plug, ex.EUStandard)
        self.assertIsNotNone(eu_plug)
        self.assertIsInstance(eu_plug, ex.UKStandardToEUStandard)

        # We shouldn't be able to adapt it to a *concrete* 'EUPlug' though.
        eu_plug = self.adapter_registry.adapt(plug, ex.EUPlug)
        self.assertIsNone(eu_plug)

        return

    def test_adapter_chaining(self):

        from apptools.adaptation.adapter_factory import AdapterFactory

        ex = self.examples

        # UKStandard->EUStandard.
        self.adapter_registry.register_adapter_factory(
            AdapterFactory(
                factory       = ex.UKStandardToEUStandard,
                from_protocol = ex.UKStandard,
                to_protocol   = ex.EUStandard
            )
        )

        # EUStandard->JapanStandard.
        self.adapter_registry.register_adapter_factory(
            AdapterFactory(
                factory       = ex.EUStandardToJapanStandard,
                from_protocol = ex.EUStandard,
                to_protocol   = ex.JapanStandard
            )
        )

        # Create a UKPlug.
        uk_plug = ex.UKPlug()

        # Adapt it to a JapanStandard via the chain.
        japan_plug = self.adapter_registry.adapt(uk_plug, ex.JapanStandard)
        self.assertIsNotNone(japan_plug)
        self.assertIsInstance(japan_plug, ex.EUStandardToJapanStandard)
        self.assert_(japan_plug.adaptee.adaptee is uk_plug)
        
        return


class TestAdapterRegistryWithABCs(_TestAdapterRegistry):
    """ Test the adapter registry with ABCs. """

    examples = apptools.adaptation.tests.abc_examples


class TestAdapterRegistryWithInterfaces(_TestAdapterRegistry):
    """ Test the adapter registry with Interfaces. """

    examples = apptools.adaptation.tests.interface_examples

#### EOF ######################################################################
