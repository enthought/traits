# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import io
import unittest

from traits.api import Any, HasTraits, Property


class Test(HasTraits):

    output_buffer = Any()

    def __value_get(self):
        return self.__dict__.get("_value", 0)

    def __value_set(self, value):
        old_value = self.__dict__.get("_value", 0)
        if value != old_value:
            self._value = value
            self.trait_property_changed("value", old_value, value)

    value = Property(__value_get, __value_set)


class Test_1(Test):
    def _value_changed(self, value):
        self.output_buffer.write(value)


class TestPropertyNotifications(unittest.TestCase):
    def test_property_notifications(self):
        output_buffer = io.StringIO()

        test_obj = Test_1(output_buffer=output_buffer)
        test_obj.value = "value_1"
        self.assertEqual(output_buffer.getvalue(), "value_1")

        test_obj.value = "value_2"
        self.assertEqual(output_buffer.getvalue(), "value_1value_2")
