# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.util.clean_strings import clean_filename

# Safe strings should only contain the following characters.
LEGAL_CHARS = set("-0123456789_abcdefghijklmnopqrstuvwxyz")


class TestCleanStrings(unittest.TestCase):
    def test_clean_filename_default(self):
        test_strings = [
            "!!!",
            "",
            " ",
            "\t/\n",
            "^!+",
        ]
        for test_string in test_strings:
            safe_string = clean_filename(test_string, "default-output")
            self.check_output(safe_string)
            self.assertEqual(safe_string, "default-output")

    def test_clean_filename_whitespace_handling(self):
        # Leading and trailing whitespace stripped.
        self.assertEqual(clean_filename(" abc "), "abc")
        self.assertEqual(clean_filename(" \t\tabc    \n"), "abc")
        # Internal whitespace turned into hyphens.
        self.assertEqual(clean_filename("well name"), "well-name")
        self.assertEqual(clean_filename("well \n name"), "well-name")
        self.assertEqual(clean_filename("well - name"), "well-name")

    def test_clean_filename_conversion_to_lowercase(self):
        test_string = "ABCdefGHI123"
        safe_string = clean_filename(test_string)
        self.assertEqual(safe_string, test_string.lower())
        self.check_output(safe_string)

    def test_clean_filename_accented_chars(self):
        test_strings = [
            "\xe4b\xe7d\xe8f",
            "a\u0308bc\u0327de\u0300f",
        ]
        for test_string in test_strings:
            safe_string = clean_filename(test_string)
            self.check_output(safe_string)
            self.assertEqual(safe_string, "abcdef")

    def test_clean_filename_all_chars(self):
        test_strings = [
            "".join(chr(n) for n in range(10000)),
            "".join(chr(n) for n in range(10000)) * 2,
            "".join(chr(n) for n in reversed(range(10000))),
        ]
        for test_string in test_strings:
            safe_string = clean_filename(test_string)
            self.check_output(safe_string)

    def check_output(self, safe_string):
        """
        Check that a supposedly safe string is actually safe.
        """
        self.assertIsInstance(safe_string, str)
        chars_in_string = set(safe_string)
        self.assertLessEqual(chars_in_string, LEGAL_CHARS)
