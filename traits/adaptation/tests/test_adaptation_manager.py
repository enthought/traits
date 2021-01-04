# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Test the adaptation manager. """

import unittest

from traits.adaptation.api import AdaptationManager
import traits.adaptation.tests.abc_examples
import traits.adaptation.tests.interface_examples


class TestAdaptationManagerWithABC(unittest.TestCase):
    """ Test the adaptation manager. """

    #: Class attribute pointing at the module containing the example data
    examples = traits.adaptation.tests.abc_examples

    #### 'TestCase' protocol ##################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        self.adaptation_manager = AdaptationManager()

    #### Tests ################################################################

    def test_no_adapter_required(self):

        ex = self.examples

        plug = ex.UKPlug()

        # Try to adapt it to its own concrete type.
        uk_plug = self.adaptation_manager.adapt(plug, ex.UKPlug)

        # The adaptation manager should simply return the same object.
        self.assertIs(uk_plug, plug)

        # Try to adapt it to an ABC that is registered for its type.
        uk_plug = self.adaptation_manager.adapt(plug, ex.UKStandard)

        # The adaptation manager should simply return the same object.
        self.assertIs(uk_plug, plug)

    def test_no_adapter_available(self):

        ex = self.examples

        plug = ex.UKPlug()

        # Try to adapt it to a concrete type.
        eu_plug = self.adaptation_manager.adapt(plug, ex.EUPlug, None)

        # There should be no way to adapt a UKPlug to a EUPlug.
        self.assertEqual(eu_plug, None)

        # Try to adapt it to an ABC.
        eu_plug = self.adaptation_manager.adapt(plug, ex.EUStandard, None)

        # There should be no way to adapt a UKPlug to a EUPlug.
        self.assertEqual(eu_plug, None)

    def test_one_step_adaptation(self):

        ex = self.examples

        # UKStandard->EUStandard.
        self.adaptation_manager.register_factory(
            factory=ex.UKStandardToEUStandard,
            from_protocol=ex.UKStandard,
            to_protocol=ex.EUStandard,
        )

        plug = ex.UKPlug()

        # Adapt it to an ABC.
        eu_plug = self.adaptation_manager.adapt(plug, ex.EUStandard)
        self.assertIsNotNone(eu_plug)
        self.assertIsInstance(eu_plug, ex.UKStandardToEUStandard)

        # We shouldn't be able to adapt it to a *concrete* 'EUPlug' though.
        eu_plug = self.adaptation_manager.adapt(plug, ex.EUPlug, None)
        self.assertIsNone(eu_plug)

    def test_adapter_chaining(self):

        ex = self.examples

        # UKStandard->EUStandard.
        self.adaptation_manager.register_factory(
            factory=ex.UKStandardToEUStandard,
            from_protocol=ex.UKStandard,
            to_protocol=ex.EUStandard,
        )

        # EUStandard->JapanStandard.
        self.adaptation_manager.register_factory(
            factory=ex.EUStandardToJapanStandard,
            from_protocol=ex.EUStandard,
            to_protocol=ex.JapanStandard,
        )

        # Create a UKPlug.
        uk_plug = ex.UKPlug()

        # Adapt it to a JapanStandard via the chain.
        japan_plug = self.adaptation_manager.adapt(uk_plug, ex.JapanStandard)
        self.assertIsNotNone(japan_plug)
        self.assertIsInstance(japan_plug, ex.EUStandardToJapanStandard)
        self.assertIs(japan_plug.adaptee.adaptee, uk_plug)

    def test_multiple_paths_unambiguous(self):

        ex = self.examples

        # UKStandard->EUStandard.
        self.adaptation_manager.register_factory(
            factory=ex.UKStandardToEUStandard,
            from_protocol=ex.UKStandard,
            to_protocol=ex.EUStandard,
        )

        # EUStandard->JapanStandard.
        self.adaptation_manager.register_factory(
            factory=ex.EUStandardToJapanStandard,
            from_protocol=ex.EUStandard,
            to_protocol=ex.JapanStandard,
        )

        # JapanStandard->IraqStandard.
        self.adaptation_manager.register_factory(
            factory=ex.JapanStandardToIraqStandard,
            from_protocol=ex.JapanStandard,
            to_protocol=ex.IraqStandard,
        )

        # EUStandard->IraqStandard.
        self.adaptation_manager.register_factory(
            factory=ex.EUStandardToIraqStandard,
            from_protocol=ex.EUStandard,
            to_protocol=ex.IraqStandard,
        )

        # Create a UKPlug.
        uk_plug = ex.UKPlug()

        # Adapt it to a IraqStandard via the chain.
        iraq_plug = self.adaptation_manager.adapt(uk_plug, ex.IraqStandard)
        self.assertIsNotNone(iraq_plug)
        self.assertIsInstance(iraq_plug, ex.EUStandardToIraqStandard)
        self.assertIs(iraq_plug.adaptee.adaptee, uk_plug)

    def test_multiple_paths_ambiguous(self):

        ex = self.examples

        # UKStandard->EUStandard.
        self.adaptation_manager.register_factory(
            factory=ex.UKStandardToEUStandard,
            from_protocol=ex.UKStandard,
            to_protocol=ex.EUStandard,
        )

        # UKStandard->JapanStandard.
        self.adaptation_manager.register_factory(
            factory=ex.UKStandardToJapanStandard,
            from_protocol=ex.UKStandard,
            to_protocol=ex.JapanStandard,
        )

        # JapanStandard->IraqStandard.
        self.adaptation_manager.register_factory(
            factory=ex.JapanStandardToIraqStandard,
            from_protocol=ex.JapanStandard,
            to_protocol=ex.IraqStandard,
        )

        # EUStandard->IraqStandard.
        self.adaptation_manager.register_factory(
            factory=ex.EUStandardToIraqStandard,
            from_protocol=ex.EUStandard,
            to_protocol=ex.IraqStandard,
        )

        # Create a UKPlug.
        uk_plug = ex.UKPlug()

        # Adapt it to a IraqStandard via the chain.
        iraq_plug = self.adaptation_manager.adapt(uk_plug, ex.IraqStandard)
        self.assertIsNotNone(iraq_plug)
        self.assertIn(
            type(iraq_plug),
            [ex.EUStandardToIraqStandard, ex.JapanStandardToIraqStandard],
        )
        self.assertIs(iraq_plug.adaptee.adaptee, uk_plug)

    def test_conditional_adaptation(self):

        ex = self.examples

        # TravelPlug->EUStandard.
        def travel_plug_to_eu_standard(adaptee):
            if adaptee.mode == "Europe":
                return ex.TravelPlugToEUStandard(adaptee=adaptee)

            else:
                return None

        self.adaptation_manager.register_factory(
            factory=travel_plug_to_eu_standard,
            from_protocol=ex.TravelPlug,
            to_protocol=ex.EUStandard,
        )

        # Create a TravelPlug.
        travel_plug = ex.TravelPlug(mode="Europe")

        # Adapt it to a EUStandard.
        eu_plug = self.adaptation_manager.adapt(travel_plug, ex.EUStandard)
        self.assertIsNotNone(eu_plug)
        self.assertIsInstance(eu_plug, ex.TravelPlugToEUStandard)

        # Create a TravelPlug.
        travel_plug = ex.TravelPlug(mode="Asia")

        # Adapt it to a EUStandard.
        eu_plug = self.adaptation_manager.adapt(
            travel_plug, ex.EUStandard, None
        )
        self.assertIsNone(eu_plug)

    def test_spillover_adaptation_behavior(self):

        ex = self.examples

        # FileType->IEditor.
        self.adaptation_manager.register_factory(
            factory=ex.FileTypeToIEditor,
            from_protocol=ex.FileType,
            to_protocol=ex.IEditor,
        )

        # Meanwhile, in a plugin far, far away ...
        # IScriptable->IPrintable.
        self.adaptation_manager.register_factory(
            factory=ex.IScriptableToIUndoable,
            from_protocol=ex.IScriptable,
            to_protocol=ex.IUndoable,
        )

        # Create a file type.
        file_type = ex.FileType()

        # Try to adapt to IPrintable: since we did not define an adapter
        # chain that goes from FileType to IPrintable, this should fail.
        printable = self.adaptation_manager.adapt(
            file_type, ex.IUndoable, None
        )
        self.assertIsNone(printable)

    def test_adaptation_prefers_subclasses(self):

        ex = self.examples

        # TextEditor->IPrintable.
        self.adaptation_manager.register_factory(
            factory=ex.TextEditorToIPrintable,
            from_protocol=ex.TextEditor,
            to_protocol=ex.IPrintable,
        )

        # Editor->IPrintable.
        self.adaptation_manager.register_factory(
            factory=ex.EditorToIPrintable,
            from_protocol=ex.Editor,
            to_protocol=ex.IPrintable,
        )

        # Create a text editor.
        text_editor = ex.TextEditor()

        # Adapt to IPrintable: we should get the TextEditorToIPrintable
        # adapter, not the EditorToIPrintable one.
        printable = self.adaptation_manager.adapt(text_editor, ex.IPrintable)
        self.assertIsNotNone(printable)
        self.assertIs(type(printable), ex.TextEditorToIPrintable)

    def test_adaptation_prefers_subclasses_other_registration_order(self):
        # This test is identical to `test_adaptation_prefers_subclasses`
        # with adapters registered in the opposite order. Both of them
        # should pass

        ex = self.examples

        # Editor->IPrintable.
        self.adaptation_manager.register_factory(
            factory=ex.EditorToIPrintable,
            from_protocol=ex.Editor,
            to_protocol=ex.IPrintable,
        )

        # TextEditor->IPrintable.
        self.adaptation_manager.register_factory(
            factory=ex.TextEditorToIPrintable,
            from_protocol=ex.TextEditor,
            to_protocol=ex.IPrintable,
        )

        # Create a text editor.
        text_editor = ex.TextEditor()

        # Adapt to IPrintable: we should get the TextEditorToIPrintable
        # adapter, not the EditorToIPrintable one.
        printable = self.adaptation_manager.adapt(text_editor, ex.IPrintable)
        self.assertIsNotNone(printable)
        self.assertIs(type(printable), ex.TextEditorToIPrintable)

    def test_circular_adaptation(self):
        # Circles in the adaptation graph should not lead to infinite loops
        # when it is impossible to reach the target.

        class Foo(object):
            pass

        class Bar(object):
            pass

        # object->Foo
        self.adaptation_manager.register_factory(
            factory=lambda adaptee: Foo(),
            from_protocol=object,
            to_protocol=Foo,
        )

        # Foo->object
        self.adaptation_manager.register_factory(
            factory=lambda adaptee: [], from_protocol=Foo, to_protocol=object
        )

        # Create an object.
        obj = []

        # Try to adapt to an unreachable target.
        bar = self.adaptation_manager.adapt(obj, Bar, None)
        self.assertIsNone(bar)

    def test_default_argument_in_adapt(self):

        from traits.adaptation.adaptation_manager import AdaptationError

        # Without a default argument, a failed adaptation raises an error.
        with self.assertRaises(AdaptationError):
            self.adaptation_manager.adapt("string", int)

        # With a default argument, a failed adaptation returns the default.
        default = "default"
        result = self.adaptation_manager.adapt("string", int, default=default)
        self.assertIs(result, default)

    def test_prefer_specific_interfaces(self):

        ex = self.examples

        # IIntermediate -> ITarget.
        self.adaptation_manager.register_factory(
            factory=ex.IIntermediateToITarget,
            from_protocol=ex.IIntermediate,
            to_protocol=ex.ITarget,
        )

        # IHuman -> IIntermediate.
        self.adaptation_manager.register_factory(
            factory=ex.IHumanToIIntermediate,
            from_protocol=ex.IHuman,
            to_protocol=ex.IIntermediate,
        )

        # IChild -> IIntermediate.
        self.adaptation_manager.register_factory(
            factory=ex.IChildToIIntermediate,
            from_protocol=ex.IChild,
            to_protocol=ex.IIntermediate,
        )

        # IPrimate -> IIntermediate.
        self.adaptation_manager.register_factory(
            factory=ex.IPrimateToIIntermediate,
            from_protocol=ex.IPrimate,
            to_protocol=ex.IIntermediate,
        )

        # Create a source.
        source = ex.Source()

        # Adapt to ITarget: we should get the adapter for the most specific
        # interface, i.e. IChildToITarget.
        target = self.adaptation_manager.adapt(source, ex.ITarget)
        self.assertIsNotNone(target)
        self.assertIs(type(target.adaptee), ex.IChildToIIntermediate)

    def test_chaining_with_intermediate_mro_climbing(self):

        ex = self.examples

        # IStart -> ISpecific.
        self.adaptation_manager.register_factory(
            factory=ex.IStartToISpecific,
            from_protocol=ex.IStart,
            to_protocol=ex.ISpecific,
        )

        # IGeneric -> IEnd.
        self.adaptation_manager.register_factory(
            factory=ex.IGenericToIEnd,
            from_protocol=ex.IGeneric,
            to_protocol=ex.IEnd,
        )

        # Create a start.
        start = ex.Start()

        # Adapt to IEnd; this should succeed going from IStart to ISpecific,
        # climbing up the MRO to IGeneric, then crossing to IEnd.
        end = self.adaptation_manager.adapt(start, ex.IEnd)
        self.assertIsNotNone(end)
        self.assertIs(type(end), ex.IGenericToIEnd)

    def test_conditional_recycling(self):
        # Test that an offer that has been considered but failed if considered
        # again at a later time, when it might succeed because of conditional
        # adaptation.

        # C -- A -fails- B
        # C -- D -- A -succeeds- B

        class A(object):
            def __init__(self, allow_adaptation):
                self.allow_adaptation = allow_adaptation

        class B(object):
            pass

        class C(object):
            pass

        class D(object):
            pass

        self.adaptation_manager.register_factory(
            factory=lambda adaptee: A(False), from_protocol=C, to_protocol=A
        )
        self.adaptation_manager.register_factory(
            factory=lambda adaptee: A(True), from_protocol=D, to_protocol=A
        )
        self.adaptation_manager.register_factory(
            factory=lambda adaptee: D(), from_protocol=C, to_protocol=D
        )

        # Conditional adapter
        def a_to_b_adapter(adaptee):
            if adaptee.allow_adaptation:
                b = B()
                b.marker = True
            else:
                b = None
            return b

        self.adaptation_manager.register_factory(
            factory=a_to_b_adapter, from_protocol=A, to_protocol=B
        )

        # Create a A
        c = C()

        # Adaptation to B should succeed through D
        b = self.adaptation_manager.adapt(c, B)
        self.assertIsNotNone(b)
        self.assertTrue(hasattr(b, "marker"))

    def test_provides_protocol_for_interface_subclass(self):

        from traits.api import Interface

        class IA(Interface):
            pass

        class IB(IA):
            pass

        self.assertTrue(self.adaptation_manager.provides_protocol(IB, IA))

    def test_register_provides(self):

        from traits.api import Interface

        class IFoo(Interface):
            pass

        obj = {}
        self.assertEqual(None, self.adaptation_manager.adapt(obj, IFoo, None))
        self.adaptation_manager.register_provides(dict, IFoo)
        self.assertEqual(obj, self.adaptation_manager.adapt(obj, IFoo))
