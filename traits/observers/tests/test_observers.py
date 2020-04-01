# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest
from unittest import mock

from traits.observers._observers import (
    NamedTraitObserver,
)
from traits.observers._observer_path import ObserverPath


class TestNamedTraitObserver(unittest.TestCase):

    def test_not_equal_notify(self):
        observer1 = NamedTraitObserver(name="foo", notify=True)
        observer2 = NamedTraitObserver(name="foo", notify=False)
        self.assertNotEqual(observer1, observer2)
        self.assertNotEqual(hash(observer1), hash(observer2))

    def test_not_equal_name(self):
        observer1 = NamedTraitObserver(name="foo", notify=True)
        observer2 = NamedTraitObserver(name="bar", notify=True)
        self.assertNotEqual(observer1, observer2)
        self.assertNotEqual(hash(observer1), hash(observer2))

    def test_equal_observers(self):
        observer1 = NamedTraitObserver(name="foo", notify=True)
        observer2 = NamedTraitObserver(name="foo", notify=True)
        self.assertEqual(observer1, observer2)
        self.assertEqual(hash(observer1), hash(observer2))

    def test_not_equal_type(self):
        observer = NamedTraitObserver(name="foo", notify=True)
        imposter = mock.Mock()
        imposter.name = "foo"
        imposter.notify = True
        self.assertNotEqual(observer, imposter)
        self.assertNotEqual(hash(observer), hash(imposter))

    def test_name_not_mutable(self):
        observer = NamedTraitObserver(name="foo", notify=True)
        with self.assertRaises(AttributeError) as exception_context:
            observer.name = "bar"
        self.assertEqual(
            str(exception_context.exception), "can't set attribute")

    def test_notify_not_mutable(self):
        observer = NamedTraitObserver(name="foo", notify=True)
        with self.assertRaises(AttributeError) as exception_context:
            observer.notify = False
        self.assertEqual(
            str(exception_context.exception), "can't set attribute")


class TestObserverPathIntegrateNamedTraitObserver(unittest.TestCase):
    """ Test integrating ObserverPath with NamedTraitObserver as nodes.
    """

    def test_observer_path_hash_with_named_listener(self):
        # Test equality + hashing using set passes.

        path1 = ObserverPath(
            node=NamedTraitObserver(name="foo", notify=True),
            nexts=[
                ObserverPath(
                    node=NamedTraitObserver(name="bar", notify=True),
                ),
            ],
        )
        path2 = ObserverPath(
            node=NamedTraitObserver(name="foo", notify=True),
            nexts=[
                ObserverPath(
                    node=NamedTraitObserver(name="bar", notify=True),
                ),
            ],
        )
        # This tests __eq__ and __hash__
        self.assertEqual(path1, path2)
