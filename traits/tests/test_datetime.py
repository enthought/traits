# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tests for the Datetime trait type.
"""

import datetime
import unittest

from traits.testing.optional_dependencies import requires_traitsui, traitsui

from traits.api import Datetime, HasStrictTraits, TraitError


#: Unix epoch
UNIX_EPOCH = datetime.datetime(1970, 1, 1, 0, 0)

#: Windows NT epoch
NT_EPOCH = datetime.datetime(1600, 1, 1, 0, 0)


class HasDatetimeTraits(HasStrictTraits):
    #: Simple case - no default, no parameters, no metadata
    simple_datetime = Datetime()

    #: Datetime with default
    epoch = Datetime(UNIX_EPOCH)

    #: Datetime with default provided via keyword.
    alternative_epoch = Datetime(default_value=NT_EPOCH)

    #: None prohibited
    none_prohibited = Datetime(allow_none=False)

    #: None allowed
    none_allowed = Datetime(allow_none=True)


class TestDatetime(unittest.TestCase):
    def test_default(self):
        obj = HasDatetimeTraits()
        self.assertEqual(obj.simple_datetime, None)
        self.assertEqual(obj.epoch, UNIX_EPOCH)
        self.assertEqual(obj.alternative_epoch, NT_EPOCH)

    def test_assign_datetime(self):
        # By default, datetime instances are permitted.
        test_datetime = datetime.datetime(1975, 2, 13)
        obj = HasDatetimeTraits()
        obj.simple_datetime = test_datetime
        self.assertEqual(obj.simple_datetime, test_datetime)

    def test_assign_non_datetime(self):
        obj = HasDatetimeTraits()
        with self.assertRaises(TraitError) as exception_context:
            obj.simple_datetime = "2021-02-05 12:00:00"
        message = str(exception_context.exception)
        self.assertIn("must be a datetime or None, but", message)

    def test_assign_date(self):
        obj = HasDatetimeTraits()
        with self.assertRaises(TraitError) as exception_context:
            obj.simple_datetime = datetime.date(1975, 2, 13)
        message = str(exception_context.exception)
        self.assertIn("must be a datetime or None, but", message)
        self.assertIsNone(obj.simple_datetime)

    def test_assign_none_with_allow_none_not_given(self):
        obj = HasDatetimeTraits(simple_datetime=UNIX_EPOCH)
        self.assertIsNotNone(obj.simple_datetime)
        with self.assertWarns(DeprecationWarning) as warnings_cm:
            obj.simple_datetime = None
        self.assertIsNone(obj.simple_datetime)

        _, _, this_module = __name__.rpartition(".")
        self.assertIn(this_module, warnings_cm.filename)
        self.assertIn(
            "None will no longer be accepted",
            str(warnings_cm.warning),
        )

    def test_assign_none_with_allow_none_false(self):
        obj = HasDatetimeTraits(none_prohibited=UNIX_EPOCH)
        with self.assertRaises(TraitError) as exception_context:
            obj.none_prohibited = None
        message = str(exception_context.exception)
        self.assertIn("must be a datetime, but", message)

    def test_assign_none_with_allow_none_true(self):
        obj = HasDatetimeTraits(none_allowed=UNIX_EPOCH)
        self.assertIsNotNone(obj.none_allowed)
        obj.none_allowed = None
        self.assertIsNone(obj.none_allowed)

    @requires_traitsui
    def test_get_editor(self):
        obj = HasDatetimeTraits()
        trait = obj.base_trait("epoch")
        editor_factory = trait.get_editor()
        self.assertIsInstance(editor_factory, traitsui.api.DatetimeEditor)
