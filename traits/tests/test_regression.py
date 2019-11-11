""" General regression tests for a variety of bugs. """
import gc
import sys
import unittest

import six
import six.moves as sm

from traits.has_traits import (
    HasStrictTraits,
    HasTraits,
    Property,
    on_trait_change,
)
from traits.trait_errors import TraitError
from traits.trait_types import Bool, DelegatesTo, Either, Instance, Int, List
from traits.testing.optional_dependencies import numpy, requires_numpy

if numpy is not None:
    from traits.trait_numeric import Array


class Dummy(HasTraits):
    x = Int(10)


def _create_subclass():
    class Subclass(HasTraits):
        pass

    return Subclass


class Dummy2(HasTraits):
    y = Int(20)
    dummy = Instance(Dummy)


class DelegateMess(HasTraits):
    dummy1 = Instance(Dummy, args=())
    dummy2 = Instance(Dummy2)

    y = DelegatesTo("dummy2")

    handler_called = Bool(False)

    def _dummy2_default(self):
        # Create `self.dummy1`
        return Dummy2(dummy=self.dummy1)

    @on_trait_change("dummy1.x")
    def _on_dummy1_x(self):
        self.handler_called = True

    def _init_trait_listeners(self):
        """ Force the DelegatesTo listener to hook up first to exercise the
        worst case.
        """
        for name in ["y", "_on_dummy1_x"]:
            data = self.__class__.__listener_traits__[name]
            getattr(self, "_init_trait_%s_listener" % data[0])(name, *data)


class DelegateLeak(HasTraits):
    visible = Property(Bool, depends_on="can_enable")

    can_enable = DelegatesTo("flag", prefix="x")

    flag = Instance(Dummy, kw={"x": 42})


class Presenter(HasTraits):
    obj = Instance(Dummy)
    y = Property(Int(), depends_on="obj.x")

    def _get_y(self):
        return self.obj.x


class ListUpdatesTest(HasTraits):
    a = List
    b = List
    events_received = Int(0)

    @on_trait_change("a[], b[]")
    def _receive_events(self):
        self.events_received += 1


class SimpleProperty(HasTraits):
    x = Int

    y = Property(Int, depends_on="x")

    def _get_y(self):
        return self.x + 1


class ExtendedListenerInList(HasTraits):
    # Used in regression test for enthought/traits#403.

    dummy = Instance(Dummy)

    changed = Bool(False)

    @on_trait_change(["dummy:x"])
    def set_changed(self):
        self.changed = True


class TestRegression(unittest.TestCase):
    def test_default_value_for_no_cache(self):
        """ Make sure that CTrait.default_value_for() does not cache the
        result.
        """
        dummy = Dummy()
        # Nothing in the __dict__ yet.
        self.assertEqual(dummy.__dict__, {})
        ctrait = dummy.trait("x")
        default = ctrait.default_value_for(dummy, "x")
        self.assertEqual(default, 10)
        self.assertEqual(dummy.__dict__, {})

    def test_default_value_for_property(self):
        """ Don't segfault when calling default_value_for on a Property trait.
        """
        # Regression test for enthought/traits#336.
        y_trait = SimpleProperty.class_traits()["y"]
        simple_property = SimpleProperty()
        self.assertIsNone(y_trait.default_value_for(simple_property, "y"))

    def test_subclasses_weakref(self):
        """ Make sure that dynamically created subclasses are not held
        strongly by HasTraits.
        """
        previous_subclasses = HasTraits.__subclasses__()
        _create_subclass()
        _create_subclass()
        _create_subclass()
        _create_subclass()
        gc.collect()
        self.assertEqual(previous_subclasses, HasTraits.__subclasses__())

    def test_leaked_property_tuple(self):
        """ the property ctrait constructor shouldn't leak a tuple. """

        class A(HasTraits):
            prop = Property()

        a = A()
        self.assertEqual(sys.getrefcount(a.trait("prop").property()), 1)

    def test_delegate_initializer(self):
        mess = DelegateMess()
        self.assertFalse(mess.handler_called)
        mess.dummy1.x = 20
        self.assertTrue(mess.handler_called)

    def test_no_leaking_notifiers(self):
        """ Extended trait change notifications should not leaf
        TraitChangeNotifyWrappers.
        """
        dummy = Dummy()
        ctrait = dummy._trait("x", 2)
        self.assertEqual(len(ctrait._notifiers(1)), 0)
        presenter = Presenter(obj=dummy)
        self.assertEqual(len(ctrait._notifiers(1)), 1)
        del presenter
        self.assertEqual(len(ctrait._notifiers(1)), 0)

    def test_init_list_depends(self):
        """ Using two lists with bracket notation in extended name notation
        should not raise an error.
        """
        list_test = ListUpdatesTest()
        # Updates to list items and the list trait itself should be counted.
        list_test.a.append(0)
        list_test.b = [1, 2, 3]
        list_test.b[0] = 0
        self.assertEqual(list_test.events_received, 3)

    def test_has_traits_notifiers_refleak(self):
        # Regression test for issue described in
        # https://github.com/enthought/traits/pull/248

        warmup = 5
        cycles = 10
        counts = []

        def handler():
            pass

        def f():
            obj = HasTraits()
            obj.on_trait_change(handler)

        # Warmup.
        for _ in sm.range(cycles):
            f()
            gc.collect()
            counts.append(len(gc.get_objects()))

        # All the counts beyond the warmup period should be the same.
        self.assertEqual(counts[warmup:-1], counts[warmup + 1 :])

    def test_delegation_refleak(self):
        warmup = 5
        cycles = 10
        counts = []

        for _ in sm.range(cycles):
            DelegateLeak()
            gc.collect()
            counts.append(len(gc.get_objects()))

        # All the counts should be the same.
        self.assertEqual(counts[warmup:-1], counts[warmup + 1 :])

    @requires_numpy
    def test_exception_from_numpy_comparison_ignored(self):
        # Regression test for enthought/traits#376.

        class MultiArrayDataSource(HasTraits):
            data = Either(None, Array)

        b = MultiArrayDataSource(data=numpy.array([1, 2]))
        # The following line was necessary to trigger the bug: the previous
        # line set a Python exception, but didn't return the correct result to
        # the CPython interpreter, so the exception wasn't triggered until
        # later.
        round(3.14159, 2)

    def test_on_trait_change_with_list_of_extended_names(self):
        # Regression test for enthought/traits#403
        dummy = Dummy(x=10)
        model = ExtendedListenerInList(dummy=dummy)
        self.assertFalse(model.changed)
        dummy.x = 11
        self.assertTrue(model.changed)

    def test_set_disallowed_exception(self):
        # Regression test for enthought/traits#415

        class StrictDummy(HasStrictTraits):
            foo = Int

        with self.assertRaises(TraitError):
            StrictDummy(forbidden=53)

        if six.PY2:
            with self.assertRaises(TraitError):
                StrictDummy(**{b"forbidden": 53})

        # This is the case that used to fail on Python 2.
        with self.assertRaises(TraitError):
            StrictDummy(**{u"forbidden": 53})

        a = StrictDummy()
        with self.assertRaises(TraitError):
            setattr(a, u"forbidden", 53)
