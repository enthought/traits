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

from traits.api import HasTraits, Int, on_trait_change


class BaseTestClass(HasTraits):
    foo = Int()
    bar = Int()
    baz = Int()
    output_name = None
    output_old = None
    output_new = None


class TestOnTraitChangeNotification(unittest.TestCase):
    """ Tests on_trait_change notifications"""

    def test_notification(self):
        class TestClass(BaseTestClass):
            @on_trait_change(',bar, baz,')
            def _report_change(self, obj, name, old, new):
                self.output_old = old
                self.output_new = new
                self.output_name = name

        obj = TestClass()
        obj.foo = 5
        # Ensure notification is not fired for foo
        self.assertIsNone(obj.output_name)
        self.assertIsNone(obj.output_new)
        self.assertIsNone(obj.output_old)

        obj.bar = 6
        # Ensure notification is fired for bar
        self.assertEqual("bar", obj.output_name)
        self.assertEqual(0, obj.output_old)
        self.assertEqual(6, obj.output_new)

        obj.baz = 6
        # Ensure notification is fired for baz
        self.assertEqual("baz", obj.output_name)
        self.assertEqual(0, obj.output_old)
        self.assertEqual(6, obj.output_new)

    def test_notification_trait_list(self):
        class TestClass(BaseTestClass):
            @on_trait_change('[foo,, baz,]')
            def _report_change(self, obj, name, old, new):
                self.output_old = old
                self.output_new = new
                self.output_name = name

        obj = TestClass()
        obj.bar = 5
        # Ensure notification is not fired for bar
        self.assertIsNone(obj.output_name)
        self.assertIsNone(obj.output_new)
        self.assertIsNone(obj.output_old)

        obj.foo = 6
        # Ensure notification is fired for foo
        self.assertEqual("foo", obj.output_name)
        self.assertEqual(0, obj.output_old)
        self.assertEqual(6, obj.output_new)

        obj.baz = 6
        # Ensure notification is fired for baz
        self.assertEqual("baz", obj.output_name)
        self.assertEqual(0, obj.output_old)
        self.assertEqual(6, obj.output_new)
