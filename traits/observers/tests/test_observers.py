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


class TestNamedTraitObserver(unittest.TestCase):

    def test_not_equal_notify(self):
        observer1 = NamedTraitObserver(name="foo", notify=True)
        observer2 = NamedTraitObserver(name="foo", notify=False)
        self.assertNotEqual(observer1, observer2)

    def test_not_equal_name(self):
        observer1 = NamedTraitObserver(name="foo", notify=True)
        observer2 = NamedTraitObserver(name="bar", notify=True)
        self.assertNotEqual(observer1, observer2)

    def test_equal_observers(self):
        observer1 = NamedTraitObserver(name="foo", notify=True)
        observer2 = NamedTraitObserver(name="foo", notify=True)
        self.assertEqual(observer1, observer2)

    def test_not_equal_type(self):
        observer = NamedTraitObserver(name="foo", notify=True)
        imposter = mock.Mock()
        imposter.name = "foo"
        imposter.notify = True
        self.assertNotEqual(observer, imposter)
