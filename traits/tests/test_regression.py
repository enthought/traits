# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" General regression tests for a variety of bugs. """
import gc
import sys
import unittest

from traits.constants import DefaultValue
from traits.has_traits import (
    HasStrictTraits,
    HasTraits,
    Property,
    on_trait_change,
)
from traits.testing.optional_dependencies import numpy, requires_numpy
from traits.trait_errors import TraitError
from traits.trait_type import TraitType
from traits.trait_types import (
    Bool,
    DelegatesTo,
    Dict,
    Either,
    Instance,
    Int,
    List,
    Set,
    Str,
    Union,
)

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


class RaisingValidator(TraitType):
    """ Trait type whose ``validate`` method raises an inappropriate exception.

    Used for testing propagation of that exception.
    """
    info_text = "bogus"

    #: The default value type to use.
    default_value_type = DefaultValue.constant

    #: The default value for the trait:
    default_value = None

    def validate(self, object, name, value):
        raise ZeroDivisionError("Just testing")


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

        # In Python < 3.6, we can end up seeing the same subclasses but in
        # a different order, so use assertCountEqual rather than assertEqual.
        # Ref: enthought/traits#1282.
        self.assertCountEqual(previous_subclasses, HasTraits.__subclasses__())

    def test_leaked_property_tuple(self):
        """ the property ctrait constructor shouldn't leak a tuple. """

        class A(HasTraits):
            prop = Property()

        a = A()
        self.assertEqual(sys.getrefcount(a.trait("prop").property_fields), 1)

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
        self.assertEqual(len(ctrait._notifiers(True)), 0)
        presenter = Presenter(obj=dummy)
        self.assertEqual(len(ctrait._notifiers(True)), 1)
        del presenter
        self.assertEqual(len(ctrait._notifiers(True)), 0)

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
        for _ in range(cycles):
            f()
            gc.collect()
            counts.append(len(gc.get_objects()))

        # All the counts beyond the warmup period should be the same.
        self.assertEqual(counts[warmup:-1], counts[warmup + 1:])

    def test_delegation_refleak(self):
        warmup = 5
        cycles = 10
        counts = []

        for _ in range(cycles):
            DelegateLeak()
            gc.collect()
            counts.append(len(gc.get_objects()))

        # All the counts should be the same.
        self.assertEqual(counts[warmup:-1], counts[warmup + 1:])

    @requires_numpy
    def test_exception_from_numpy_comparison_ignored(self):
        # Regression test for enthought/traits#376.

        class MultiArrayDataSource(HasTraits):
            data = Either(None, Array)

        b = MultiArrayDataSource(data=numpy.array([1, 2]))  # noqa: F841
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

        # This is the case that used to fail on Python 2.
        with self.assertRaises(TraitError):
            StrictDummy(**{"forbidden": 53})

        a = StrictDummy()
        with self.assertRaises(TraitError):
            setattr(a, "forbidden", 53)

    def test_validate_exception_propagates(self):
        class A(HasTraits):
            foo = RaisingValidator()

            bar = Either(None, RaisingValidator())

        a = A()
        with self.assertRaises(ZeroDivisionError):
            a.foo = "foo"

        with self.assertRaises(ZeroDivisionError):
            a.bar = "foo"


class NestedContainerClass(HasTraits):
    # Used in regression test for changes to nested containers

    # Nested list
    list_of_list = List(List)

    # enthought/traits#281
    dict_of_list = Dict(Str, List(Str))

    # Similar to enthought/traits#281
    dict_of_union_none_or_list = Dict(Str, Union(List(), None))

    # Nested dict
    # enthought/traits#25
    list_of_dict = List(Dict)

    dict_of_dict = Dict(Str, Dict)

    dict_of_union_none_or_dict = Dict(Str, Union(Dict(), None))

    # Nested set
    list_of_set = List(Set)

    dict_of_set = Dict(Str, Set)

    dict_of_union_none_or_set = Dict(Str, Union(Set(), None))


class TestRegressionNestedContainerEvent(unittest.TestCase):
    """ Regression tests for enthought/traits#281 and enthought/traits#25
    """

    def setUp(self):
        self.events = []

        def change_handler(*args):
            self.events.append(args)

        self.change_handler = change_handler

    def test_modify_list_in_dict(self):
        # Regression test for enthought/traits#281
        instance = NestedContainerClass(dict_of_list={"name": []})

        try:
            instance.dict_of_list["name"].append("word")
        except Exception:
            self.fail("Mutating a nested list should not fail.")

    def test_modify_list_in_dict_wrapped_in_union(self):
        instance = NestedContainerClass(
            dict_of_union_none_or_list={"name": []},
        )
        try:
            instance.dict_of_union_none_or_list["name"].append("word")
        except Exception:
            self.fail("Mutating a nested list should not fail.")

    def test_modify_list_in_list_no_events(self):
        instance = NestedContainerClass(list_of_list=[[]])
        instance.on_trait_change(self.change_handler, "list_of_list_items")

        instance.list_of_list[0].append(1)
        self.assertEqual(len(self.events), 0, "Expected no events.")

    def test_modify_dict_in_list(self):
        instance = NestedContainerClass(list_of_dict=[{}])

        try:
            instance.list_of_dict[0]["key"] = 1
        except Exception:
            self.fail("Mutating a nested dict should not fail.")

    def test_modify_dict_in_list_with_new_value(self):
        instance = NestedContainerClass(list_of_dict=[{}])

        instance.list_of_dict.append(dict())
        try:
            instance.list_of_dict[-1]["key"] = 1
        except Exception:
            self.fail("Mutating a nested dict should not fail.")

    def test_modify_dict_in_dict_no_events(self):
        # Related to enthought/traits#25
        instance = NestedContainerClass(dict_of_dict={"1": {"2": 2}})
        instance.on_trait_change(self.change_handler, "dict_of_dict_items")

        instance.dict_of_dict["1"]["3"] = 3

        self.assertEqual(len(self.events), 0, "Expected no events.")

    def test_modify_dict_in_union_in_dict_no_events(self):
        instance = NestedContainerClass(
            dict_of_union_none_or_dict={"1": {"2": 2}},
        )
        instance.on_trait_change(
            self.change_handler, "dict_of_union_none_or_dict_items")

        instance.dict_of_union_none_or_dict["1"]["3"] = 3

        self.assertEqual(len(self.events), 0, "Expected no events.")

    def test_modify_set_in_list(self):
        instance = NestedContainerClass(list_of_set=[set()])
        try:
            instance.list_of_set[0].add(1)
        except Exception:
            self.fail("Mutating a nested set should not fail.")

    def test_modify_set_in_list_with_new_value(self):
        instance = NestedContainerClass(list_of_set=[])
        instance.list_of_set.append(set())
        try:
            instance.list_of_set[0].add(1)
        except Exception:
            self.fail("Mutating a nested set should not fail.")

    def test_modify_set_in_dict(self):
        instance = NestedContainerClass(dict_of_set={"1": set()})
        try:
            instance.dict_of_set["1"].add(1)
        except Exception:
            self.fail("Mutating a nested set should not fail.")

    def test_modify_set_in_union_in_dict(self):
        instance = NestedContainerClass(
            dict_of_union_none_or_set={"1": set()}
        )
        try:
            instance.dict_of_union_none_or_set["1"].add(1)
        except Exception:
            self.fail("Mutating a nested set should not fail.")

    def test_modify_nested_set_no_events(self):
        instance = NestedContainerClass(list_of_set=[set()])
        instance.on_trait_change(
            self.change_handler, "list_of_set_items")

        instance.list_of_set[0].add(1)

        self.assertEqual(len(self.events), 0, "Expected no events.")
