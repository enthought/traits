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
    #: Cake expiry date
    expiry = Date(allow_datetime=False)

    #: Datetime allowed!
    solstice = Date(allow_datetime=True)

    #: Date with default
    epoch = Date(UNIX_EPOCH)

    #: Date with default spelled out explicitly using the keyword.
    alternative_epoch = Date(default_value=NT_EPOCH)


class TestDate(unittest.TestCase):
    def test_default(self):
        obj = HasDateTraits()
        self.assertEqual(obj.epoch, UNIX_EPOCH)
        self.assertEqual(obj.alternative_epoch, NT_EPOCH)
        self.assertEqual(obj.expiry, None)

    def test_assign_a_date(self):
        test_date = datetime.date(1975, 2, 13)
        obj = HasDateTraits()
        obj.expiry = test_date
        self.assertEqual(obj.expiry, test_date)

    def test_assign_not_a_date(self):
        obj = HasDateTraits()
        with self.assertRaises(TraitError):
            obj.expiry = "1975-2-13"

    def test_info_text(self):
        obj = HasDateTraits()
        with self.assertRaises(TraitError) as exception_context:
            obj.solstice = "1975-2-13"
        message = str(exception_context.exception)
        self.assertIn("must be a date or None", message)

    def test_assign_none(self):
        # This is a test for the current behaviour. There may be an argument
        # for optionally disallowing None. Note that specifying
        # allow_none=False in the trait definition does not work as expected.
        obj = HasDateTraits(expiry=UNIX_EPOCH)
        obj.expiry = None
        self.assertIsNone(obj.expiry)

    def test_assign_a_datetime_legacy(self):
        # Legacy case: by default, datetime instances are permitted.
        test_datetime = datetime.datetime(1975, 2, 13)
        obj = HasDateTraits()
        obj.solstice = test_datetime
        self.assertEqual(obj.solstice, test_datetime)

    @requires_traitsui
    def test_get_editor(self):
        obj = HasDateTraits()
        trait = obj.base_trait("epoch")
        editor_factory = trait.get_editor()
        self.assertIsInstance(editor_factory, traitsui.api.DateEditor)

    def test_disallow_datetime(self):
        test_datetime = datetime.datetime(1975, 2, 13)
        obj = HasDateTraits()
        with self.assertRaises(TraitError) as exception_context:
            obj.expiry = test_datetime
        message = str(exception_context.exception)
        self.assertIn("must be a non-datetime date or None", message)
