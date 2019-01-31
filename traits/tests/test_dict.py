#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
""" Test cases for dictionary (Dict) traits. """

from __future__ import absolute_import

import unittest

from traits.trait_types import Dict, Event, Str, TraitDictObject
from traits.has_traits import HasTraits, on_trait_change
from traits.trait_errors import TraitError


# fixme: We'd like to use a callable instance for the listener so that we
# can maintain state, but traits barfs trying to determine the signature 8^()
def create_listener():
    """ Create a listener for testing trait notifications. """

    def listener(obj, trait_name, old, new):

        listener.obj = obj
        listener.trait_name = trait_name
        listener.new = new
        listener.old = old
        listener.called += 1
        return

    listener.initialize = lambda: initialize_listener(listener)
    return initialize_listener(listener)


def initialize_listener(listener):
    """ Initialize a listener so it looks like it hasn't been called.

    This allows us to re-use the listener without having to create and
    wire-up a new one.

    """

    listener.obj = None
    listener.trait_name = None
    listener.old = None
    listener.new = None
    listener.called = 0

    return listener  # For convenience


class TestDict(unittest.TestCase):
    """ Test cases for dictionary (Dict) traits. """

    def test_modified_event(self):
        class Foo(HasTraits):
            name = Str
            modified = Event

            @on_trait_change("name")
            def _fire_modified_event(self):
                self.modified = True
                return

        class Bar(HasTraits):
            foos = Dict(Str, Foo)
            modified = Event

            @on_trait_change("foos_items,foos.modified")
            def _fire_modified_event(self, obj, trait_name, old, new):
                self.modified = True
                return

        bar = Bar()
        listener = create_listener()
        bar.on_trait_change(listener, "modified")

        # Assign a completely new dictionary.
        bar.foos = {"dino": Foo(name="dino")}
        self.assertEqual(1, listener.called)
        self.assertEqual("modified", listener.trait_name)

        # Add an item to an existing dictionary.
        listener.initialize()
        fred = Foo(name="fred")
        bar.foos["fred"] = fred
        self.assertEqual(1, listener.called)
        self.assertEqual("modified", listener.trait_name)

        # Modify an item already in the dictionary.
        listener.initialize()
        fred.name = "barney"
        self.assertEqual(1, listener.called)
        self.assertEqual("modified", listener.trait_name)

        # Overwrite an item in the dictionary. This is the one that fails!
        listener.initialize()
        bar.foos["fred"] = Foo(name="wilma")
        self.assertEqual(1, listener.called)
        self.assertEqual("modified", listener.trait_name)

        return

    def test_validate(self):
        """ Check the validation method.

        """
        foo = Dict()

        # invalid value
        with self.assertRaises(TraitError):
            foo.validate(object=HasTraits(), name="bar", value=None)

        # valid value
        result = foo.validate(object=HasTraits(), name="bar", value={})
        self.assertIsInstance(result, TraitDictObject)

        # object is None (check for issue #71)
        result = foo.validate(object=None, name="bar", value={})
        self.assertEqual(result, {})
