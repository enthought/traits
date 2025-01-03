# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tests for the Date trait type.
"""

import datetime
import unittest

from traits.testing.optional_dependencies import requires_traitsui, traitsui

from traits.api import Date, HasStrictTraits, TraitError


#: Unix epoch date.
UNIX_EPOCH = datetime.date(1970, 1, 1)

#: Windows NT epoch
NT_EPOCH = datetime.date(1600, 1, 1)


class HasDateTraits(HasStrictTraits):
    #: Simple case - no default, no parameters, no metadata
    simple_date = Date()

    #: Date with default
    epoch = Date(UNIX_EPOCH)

    #: Date with default provided via keyword.
    alternative_epoch = Date(default_value=NT_EPOCH)

    #: Datetime instances prohibited
    datetime_prohibited = Date(allow_datetime=False)

    #: Datetime instances allowed
    datetime_allowed = Date(allow_datetime=True)

    #: None prohibited
    none_prohibited = Date(allow_none=False)

    #: None allowed
    none_allowed = Date(allow_none=True)

    #: Strictly a non-None non-datetime date
    strict = Date(allow_datetime=False, allow_none=False)


class TestDate(unittest.TestCase):
    def test_default(self):
        obj = HasDateTraits()
        self.assertEqual(obj.simple_date, None)
        self.assertEqual(obj.epoch, UNIX_EPOCH)
        self.assertEqual(obj.alternative_epoch, NT_EPOCH)

    def test_assign_date(self):
        test_date = datetime.date(1975, 2, 13)
        obj = HasDateTraits()
        obj.simple_date = test_date
        self.assertEqual(obj.simple_date, test_date)

    def test_assign_non_date(self):
        obj = HasDateTraits()
        with self.assertRaises(TraitError) as exception_context:
            obj.simple_date = "1975-2-13"
        message = str(exception_context.exception)
        self.assertIn("must be a non-datetime date, but", message)

    def test_assign_none_with_allow_none_not_given(self):
        obj = HasDateTraits(simple_date=UNIX_EPOCH)
        with self.assertRaises(TraitError) as exception_context:
            obj.simple_date = None
        self.assertEqual(obj.simple_date, UNIX_EPOCH)
        message = str(exception_context.exception)
        self.assertIn("must be a non-datetime date, but", message)

    def test_assign_none_with_allow_none_false(self):
        obj = HasDateTraits(none_prohibited=UNIX_EPOCH)
        with self.assertRaises(TraitError) as exception_context:
            obj.none_prohibited = None
        message = str(exception_context.exception)
        self.assertIn("must be a non-datetime date, but", message)

    def test_assign_none_with_allow_none_true(self):
        obj = HasDateTraits(none_allowed=UNIX_EPOCH)
        self.assertIsNotNone(obj.none_allowed)
        obj.none_allowed = None
        self.assertIsNone(obj.none_allowed)

    def test_assign_datetime_with_allow_datetime_false(self):
        test_datetime = datetime.datetime(1975, 2, 13)
        obj = HasDateTraits()
        with self.assertRaises(TraitError) as exception_context:
            obj.datetime_prohibited = test_datetime
        message = str(exception_context.exception)
        self.assertIn("must be a non-datetime date, but", message)

    def test_assign_datetime_with_allow_datetime_true(self):
        test_datetime = datetime.datetime(1975, 2, 13)
        obj = HasDateTraits()
        obj.datetime_allowed = test_datetime
        self.assertEqual(obj.datetime_allowed, test_datetime)

    def test_assign_datetime_with_allow_datetime_not_given(self):
        # For traits where "allow_datetime" is not specified, a
        # DeprecationWarning should be issued on assignment of datetime.
        test_date = datetime.date(2023, 1, 11)
        test_datetime = datetime.datetime(1975, 2, 13)
        obj = HasDateTraits(simple_date=test_date)
        with self.assertRaises(TraitError) as exception_context:
            obj.simple_date = test_datetime
        self.assertEqual(obj.simple_date, test_date)
        message = str(exception_context.exception)
        self.assertIn("must be a non-datetime date, but", message)

    def test_allow_none_false_allow_datetime_false(self):
        obj = HasDateTraits(strict=UNIX_EPOCH)
        with self.assertRaises(TraitError) as exception_context:
            obj.strict = None
        message = str(exception_context.exception)
        self.assertIn("must be a non-datetime date, but", message)

    @requires_traitsui
    def test_get_editor(self):
        obj = HasDateTraits()
        trait = obj.base_trait("epoch")
        editor_factory = trait.get_editor()
        self.assertIsInstance(editor_factory, traitsui.api.DateEditor)
