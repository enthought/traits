""" Test the adapter registry. """


import unittest

from apptools.adaptation.adapter_registry import AdapterRegistry
import apptools.adaptation.tests.abc_examples
import apptools.adaptation.tests.interface_examples


class _TestAdapterRegistry(object):
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

        ex = self.examples

        # UKStandard->EUStandard.
        self.adapter_registry.register_adapter_factory(
            factory       = ex.UKStandardToEUStandard,
            from_protocol = ex.UKStandard,
            to_protocol   = ex.EUStandard
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

        ex = self.examples

        # UKStandard->EUStandard.
        self.adapter_registry.register_adapter_factory(
            factory       = ex.UKStandardToEUStandard,
            from_protocol = ex.UKStandard,
            to_protocol   = ex.EUStandard
        )

        # EUStandard->JapanStandard.
        self.adapter_registry.register_adapter_factory(
            factory       = ex.EUStandardToJapanStandard,
            from_protocol = ex.EUStandard,
            to_protocol   = ex.JapanStandard
        )

        # Create a UKPlug.
        uk_plug = ex.UKPlug()

        # Adapt it to a JapanStandard via the chain.
        japan_plug = self.adapter_registry.adapt(uk_plug, ex.JapanStandard)
        self.assertIsNotNone(japan_plug)
        self.assertIsInstance(japan_plug, ex.EUStandardToJapanStandard)
        self.assert_(japan_plug.adaptee.adaptee is uk_plug)
        
        return

    def test_multiple_paths_unambiguous(self):

        ex = self.examples

        # UKStandard->EUStandard.
        self.adapter_registry.register_adapter_factory(
            factory       = ex.UKStandardToEUStandard,
            from_protocol = ex.UKStandard,
            to_protocol   = ex.EUStandard
        )

        # EUStandard->JapanStandard.
        self.adapter_registry.register_adapter_factory(
            factory       = ex.EUStandardToJapanStandard,
            from_protocol = ex.EUStandard,
            to_protocol   = ex.JapanStandard
        )

        # JapanStandard->IraqStandard.
        self.adapter_registry.register_adapter_factory(
            factory       = ex.JapanStandardToIraqStandard,
            from_protocol = ex.JapanStandard,
            to_protocol   = ex.IraqStandard
        )

        # EUStandard->IraqStandard.
        self.adapter_registry.register_adapter_factory(
            factory       = ex.EUStandardToIraqStandard,
            from_protocol = ex.EUStandard,
            to_protocol   = ex.IraqStandard
        )

        # Create a UKPlug.
        uk_plug = ex.UKPlug()

        # Adapt it to a IraqStandard via the chain.
        iraq_plug = self.adapter_registry.adapt(uk_plug, ex.IraqStandard)
        self.assertIsNotNone(iraq_plug)
        self.assertIsInstance(iraq_plug, ex.EUStandardToIraqStandard)
        self.assert_(iraq_plug.adaptee.adaptee is uk_plug)

        return

    def test_multiple_paths_ambiguous(self):

        ex = self.examples

        # UKStandard->EUStandard.
        self.adapter_registry.register_adapter_factory(
            factory       = ex.UKStandardToEUStandard,
            from_protocol = ex.UKStandard,
            to_protocol   = ex.EUStandard
        )

        # UKStandard->JapanStandard.
        self.adapter_registry.register_adapter_factory(
            factory       = ex.UKStandardToJapanStandard,
            from_protocol = ex.UKStandard,
            to_protocol   = ex.JapanStandard
        )

        # JapanStandard->IraqStandard.
        self.adapter_registry.register_adapter_factory(
            factory       = ex.JapanStandardToIraqStandard,
            from_protocol = ex.JapanStandard,
            to_protocol   = ex.IraqStandard
        )

        # EUStandard->IraqStandard.
        self.adapter_registry.register_adapter_factory(
            factory       = ex.EUStandardToIraqStandard,
            from_protocol = ex.EUStandard,
            to_protocol   = ex.IraqStandard
        )

        # Create a UKPlug.
        uk_plug = ex.UKPlug()

        # Adapt it to a IraqStandard via the chain.
        iraq_plug = self.adapter_registry.adapt(uk_plug, ex.IraqStandard)
        self.assertIsNotNone(iraq_plug)
        self.assertIn(
            type(iraq_plug),
            [ex.EUStandardToIraqStandard, ex.JapanStandardToIraqStandard]
        )
        self.assert_(iraq_plug.adaptee.adaptee is uk_plug)

        return

    def test_conditional_adaptation(self):

        ex = self.examples

        # TravelPlug->EUStandard.
        def travel_plug_to_eu_standard(adaptee):
            if adaptee.mode == 'Europe':
                return ex.TravelPlugToEUStandard(adaptee=adaptee)

            else:
                return None

        self.adapter_registry.register_adapter_factory(
            factory       = travel_plug_to_eu_standard,
            from_protocol = ex.TravelPlug,
            to_protocol   = ex.EUStandard
        )

        # Create a TravelPlug.
        travel_plug = ex.TravelPlug(mode='Europe')

        # Adapt it to a EUStandard.
        eu_plug = self.adapter_registry.adapt(travel_plug, ex.EUStandard)
        self.assertIsNotNone(eu_plug)
        self.assertIsInstance(eu_plug, ex.TravelPlugToEUStandard)

        # Create a TravelPlug.
        travel_plug = ex.TravelPlug(mode='Asia')

        # Adapt it to a EUStandard.
        eu_plug = self.adapter_registry.adapt(travel_plug, ex.EUStandard)
        self.assertIsNone(eu_plug)

        return

    # skip
    def test_spillover_adaptation_bug(self):
        # We skip this test: all the example we could come up with for this
        # problem are cases of bad design, and without a good use case it's
        # unclear what the right behavior should be.

        ex = self.examples

        # FileType->IEditor.
        self.adapter_registry.register_adapter_factory(
            factory       = ex.FileTypeToIEditor,
            from_protocol = ex.FileType,
            to_protocol   = ex.IEditor
        )

        # Meanwhile, in a plugin far, far away ...
        # IScriptable->IPrintable.
        self.adapter_registry.register_adapter_factory(
            factory       = ex.IScriptableToIUndoable,
            from_protocol = ex.IScriptable,
            to_protocol   = ex.IUndoable
        )

        # Create a file type.
        file_type = ex.FileType()

        # Try to adapt to IPrintable: since we did not define an adapter
        # chain that goes from FileType to IPrintable, this should fail.
        printable = self.adapter_registry.adapt(file_type, ex.IUndoable)
        self.assertIsNone(printable)

        return

    def test_adaptation_prefers_subclasses(self):

        ex = self.examples

        # BarChild->IFoo.
        self.adapter_registry.register_adapter_factory(
            factory       = ex.TextEditorToIPrintable,
            from_protocol = ex.TextEditor,
            to_protocol   = ex.IPrintable
        )

        # Bar->IFoo.
        self.adapter_registry.register_adapter_factory(
            factory       = ex.EditorToIPrintable,
            from_protocol = ex.Editor,
            to_protocol   = ex.IPrintable
        )

        # Create a text editor.
        text_editor = ex.TextEditor()

        # Adapt to IFoo: we should get the BarChildToIFoo adapter, not the
        # BarToIFoo one.
        foo = self.adapter_registry.adapt(text_editor, ex.IPrintable)
        self.assertIsNotNone(foo)
        self.assertIs(type(foo), ex.TextEditorToIPrintable)


class TestAdapterRegistryWithABCs(_TestAdapterRegistry, unittest.TestCase):
    """ Test the adapter registry with ABCs. """

    examples = apptools.adaptation.tests.abc_examples

    @unittest.skip("We are not sure what the right behavior is in this case.")
    def test_spillover_adaptation_bug(self):
        super(TestAdapterRegistryWithABCs, self).test_spillover_adaptation_bug()



class TestAdapterRegistryWithInterfaces(_TestAdapterRegistry,unittest.TestCase):
    """ Test the adapter registry with Interfaces. """

    examples = apptools.adaptation.tests.interface_examples

    @unittest.skip("We are not sure what the right behavior is in this case.")
    def test_spillover_adaptation_bug(self):
        super(TestAdapterRegistryWithInterfaces, self).test_spillover_adaptation_bug()

#### EOF ######################################################################
