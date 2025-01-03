# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.util.event_tracer import (
    SentinelRecord,
    ChangeMessageRecord,
    CallingMessageRecord,
    ExitMessageRecord,
)


class TestMessageRecords(unittest.TestCase):
    def test_base_message_record(self):
        record = SentinelRecord()

        # Check str output
        self.assertEqual(str(record), "\n")

        # Check initialization
        self.assertRaises(TypeError, SentinelRecord, sdd=0)

    def test_change_message_record(self):
        record = ChangeMessageRecord(
            time=1, indent=3, name="john", old=1, new=1, class_name="MyClass"
        )

        # Check str output
        self.assertEqual(
            str(record),
            "1 -----> 'john' changed from 1 to 1 in 'MyClass'\n",
        )

        # Check initialization
        self.assertRaises(TypeError, ChangeMessageRecord, sdd=0)

    def test_exit_message_record(self):
        record = ExitMessageRecord(
            time=7, indent=5, handler="john", exception="sssss"
        )

        # Check str output
        self.assertEqual(
            str(record), "7 <--------- EXIT: 'john'sssss\n"
        )

        # Check initialization
        self.assertRaises(TypeError, ExitMessageRecord, sdd=0)

    def test_calling_message_record(self):
        record = CallingMessageRecord(
            time=7, indent=5, handler="john", source="sssss"
        )

        # Check str output
        self.assertEqual(
            str(record), "7             CALLING: 'john' in sssss\n"
        )

        # Check initialization
        self.assertRaises(TypeError, CallingMessageRecord, sdd=0)
