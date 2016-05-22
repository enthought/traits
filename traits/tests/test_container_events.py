#------------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#------------------------------------------------------------------------------

"""
Tests for Dict items_changed events
"""

from __future__ import absolute_import

from traits.testing.unittest_tools import unittest

from ..api import HasTraits, Dict


class MyClass(HasTraits):
    """ A dummy HasTraits class with a Dict """
    d = Dict({"a": "apple", "b": "banana", "c": "cherry", "d": "durian"})

    def __init__(self, callback):
        "The callback is called with the TraitDictEvent instance"
        self.callback = callback
        return

    def _d_items_changed(self, event):
        if self.callback:
            self.callback(event)
        return


class MyOtherClass(HasTraits):
    """ A dummy HasTraits class with a Dict """
    d = Dict({"a": "apple", "b": "banana", "c": "cherry", "d": "durian"})


class Callback:
    """
    A stateful callback that gets initialized with the values to check for
    """
    def __init__(self, obj, added={}, changed={}, removed={}):
        self.obj = obj
        self.added = added
        self.changed = changed
        self.removed = removed
        self.called = False
        return

    def __call__(self, event):
        if event.added != self.added:
            print "\n\n******Error\nevent.added:", event.added
        else:
            self.obj.assertEqual(event.added, self.added)
        self.obj.assertEqual(event.changed, self.changed)
        self.obj.assertEqual(event.removed, self.removed)
        self.called = True
        return


class DictEventTestCase(unittest.TestCase):

    def test_setitem(self):
        # overwriting an existing item
        cb = Callback(self, changed={"c": "cherry"})
        foo = MyClass(cb)
        foo.d["c"] = "coconut"
        self.assertTrue(cb.called)
        # adding a new item
        cb = Callback(self, added={"g": "guava"})
        bar = MyClass(cb)
        bar.d["g"] = "guava"
        self.assertTrue(cb.called)
        return

    def test_delitem(self):
        cb = Callback(self, removed={"b": "banana"})
        foo = MyClass(cb)
        del foo.d["b"]
        self.assertTrue(cb.called)
        return

    def test_clear(self):
        removed = MyClass(None).d.copy()
        cb = Callback(self, removed=removed)
        foo = MyClass(cb)
        foo.d.clear()
        self.assertTrue(cb.called)
        return

    def test_update(self):
        update_dict = {"a": "artichoke", "f": "fig"}
        cb = Callback(self, changed={"a": "apple"}, added={"f": "fig"})
        foo = MyClass(cb)
        foo.d.update(update_dict)
        self.assertTrue(cb.called)
        return

    def test_setdefault(self):
        # Test retrieving an existing value
        cb = Callback(self)
        foo = MyClass(cb)
        self.assertEqual(foo.d.setdefault("a", "dummy"), "apple")
        self.assertFalse(cb.called)

        # Test adding a new value
        cb = Callback(self, added={"f": "fig"})
        bar = MyClass(cb)
        self.assertTrue(bar.d.setdefault("f", "fig") == "fig")
        self.assertTrue(cb.called)
        return

    def test_pop(self):
        # Test popping a non-existent key
        cb = Callback(self)
        foo = MyClass(cb)
        self.assertEqual(foo.d.pop("x", "dummy"), "dummy")
        self.assertFalse(cb.called)

        # Test popping a regular item
        cb = Callback(self, removed={"c": "cherry"})
        bar = MyClass(cb)
        self.assertEqual(bar.d.pop("c"), "cherry")
        self.assertTrue(cb.called)
        return

    def test_popitem(self):
        foo = MyClass(None)
        foo.d.clear()
        foo.d["x"] = "xylophone"
        cb = Callback(self, removed={"x": "xylophone"})
        foo.callback = cb
        self.assertEqual(foo.d.popitem(), ("x", "xylophone"))
        self.assertTrue(cb.called)
        return

    def test_dynamic_listener(self):
        foo = MyOtherClass()
        # Test adding
        func = Callback(self, added={"g": "guava"})
        foo.on_trait_change(func.__call__, "d_items")
        foo.d["g"] = "guava"
        foo.on_trait_change(func.__call__, "d_items", remove=True)
        self.assertTrue(func.called)

        # Test removing
        func2 = Callback(self, removed={"a": "apple"})
        foo.on_trait_change(func2.__call__, "d_items")
        del foo.d["a"]
        foo.on_trait_change(func2.__call__, "d_items", remove=True)
        self.assertTrue(func2.called)

        # Test changing
        func3 = Callback(self, changed={"b": "banana"})
        foo.on_trait_change(func3.__call__, "d_items")
        foo.d["b"] = "broccoli"
        foo.on_trait_change(func3.__call__, "d_items", remove=True)
        self.assertTrue(func3.called)
        return
