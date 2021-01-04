# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tests for regular Python properties in a HasTraits subclass. """

import unittest

from traits.api import HasTraits


class Model(HasTraits):
    def __init__(self):
        super().__init__()
        self._value = 0

    @property
    def read_only(self):
        return 1729

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new):
        self._value = new


class TestPythonProperty(unittest.TestCase):
    def test_read_only_property(self):
        model = Model()
        self.assertEqual(model.read_only, 1729)

        with self.assertRaises(AttributeError):
            model.read_only = 2034

        with self.assertRaises(AttributeError):
            del model.read_only

    def test_read_write_property(self):
        model = Model()
        self.assertEqual(model.value, 0)
        model.value = 23
        self.assertEqual(model.value, 23)
        model.value = 77
        self.assertEqual(model.value, 77)

        with self.assertRaises(AttributeError):
            del model.value
