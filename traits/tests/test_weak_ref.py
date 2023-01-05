# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Test cases for weakref (WeakRef) traits. """

import contextlib
import gc
import unittest

from traits.has_traits import HasTraits
from traits.trait_types import Str, WeakRef
from traits.testing.unittest_tools import UnittestTools


class Eggs(HasTraits):
    name = Str


class Spam(HasTraits):
    eggs = WeakRef(Eggs)


@contextlib.contextmanager
def restore_gc_state():
    """Ensure that gc state is restored on exit of the with statement."""
    originally_enabled = gc.isenabled()
    try:
        yield
    finally:
        if originally_enabled:
            gc.enable()
        else:
            gc.disable()


class TestWeakRef(UnittestTools, unittest.TestCase):
    """ Test cases for weakref (WeakRef) traits. """

    def test_set_and_get(self):
        eggs = Eggs(name="platypus")
        spam = Spam()
        self.assertIsNone(spam.eggs)
        spam.eggs = eggs
        self.assertIs(spam.eggs, eggs)
        del eggs
        self.assertIsNone(spam.eggs)

    def test_target_freed_notification(self):
        eggs = Eggs(name="duck")
        spam = Spam(eggs=eggs)

        # Removal of the last reference to 'eggs' should trigger notification.
        with self.assertTraitChanges(spam, "eggs"):
            del eggs

    def test_weakref_trait_doesnt_leak_cycles(self):
        eggs = Eggs(name="ostrich")
        with restore_gc_state():
            gc.disable()
            gc.collect()
            spam = Spam(eggs=eggs)
            del spam
            self.assertEqual(gc.collect(), 0)
