# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tests for the Time trait type.
"""

import datetime
import unittest

from traits.testing.optional_dependencies import requires_traitsui, traitsui

from traits.api import HasStrictTraits, Time, TraitError


#: Unix epoch
UNIX_EPOCH = datetime.time(12, 30)

#: Windows NT epoch
NT_EPOCH = datetime.time(18, 30)


class HasTimeTraits(HasStrictTraits):
    #: Simple case - no default, no parameters, no metadata
    simple_time = Time()

    #: Time with default
    epoch = Time(UNIX_EPOCH)

    #: Time with default provided via keyword.
    alternative_epoch = Time(default_value=NT_EPOCH)

    #: None prohibited
    none_prohibited = Time(allow_none=False)

    #: None allowed
    none_allowed = Time(allow_none=True)


class TestTime(unittest.TestCase):
    def test_default(self):
        obj = HasTimeTraits()
        self.assertEqual(obj.simple_time, None)
        self.assertEqual(obj.epoch, UNIX_EPOCH)
        self.assertEqual(obj.alternative_epoch, NT_EPOCH)

    def test_assign_time(self):
        # By default, datetime instances are permitted.
        test_time = datetime.time(6, 3, 35)
        obj = HasTimeTraits()
        obj.simple_time = test_time
        self.assertEqual(obj.simple_time, test_time)

    def test_assign_non_time(self):
        obj = HasTimeTraits()
        with self.assertRaises(TraitError) as exception_context:
            obj.simple_time = "12:00:00"
        message = str(exception_context.exception)
        self.assertIn("must be a time or None, but", message)

    def test_assign_datetime(self):
        obj = HasTimeTraits()
        with self.assertRaises(TraitError) as exception_context:
            obj.simple_time = datetime.datetime(1975, 2, 13)
        message = str(exception_context.exception)
        self.assertIn("must be a time or None, but", message)
        self.assertIsNone(obj.simple_time)

    def test_assign_none_with_allow_none_not_given(self):
        obj = HasTimeTraits(simple_time=UNIX_EPOCH)
        self.assertIsNotNone(obj.simple_time)
        with self.assertWarns(DeprecationWarning) as warnings_cm:
            obj.simple_time = None
        self.assertIsNone(obj.simple_time)

        _, _, this_module = __name__.rpartition(".")
        self.assertIn(this_module, warnings_cm.filename)
        self.assertIn(
            "None will no longer be accepted",
            str(warnings_cm.warning),
        )

    def test_assign_none_with_allow_none_false(self):
        obj = HasTimeTraits(none_prohibited=UNIX_EPOCH)
        with self.assertRaises(TraitError) as exception_context:
            obj.none_prohibited = None
        message = str(exception_context.exception)
        self.assertIn("must be a time, but", message)

    def test_assign_none_with_allow_none_true(self):
        obj = HasTimeTraits(none_allowed=UNIX_EPOCH)
        self.assertIsNotNone(obj.none_allowed)
        obj.none_allowed = None
        self.assertIsNone(obj.none_allowed)

    @requires_traitsui
    def test_get_editor(self):
        obj = HasTimeTraits()
        trait = obj.base_trait("epoch")
        editor_factory = trait.get_editor()
        self.assertIsInstance(editor_factory, traitsui.api.TimeEditor)
