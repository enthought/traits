#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt

from __future__ import absolute_import, print_function, unicode_literals

import unittest

import six

from traits._py2to3 import str_find, str_rfind


class TestPy2to3(unittest.TestCase):
    def test_str_find(self):
        # Note: inputs are Unicode strings.
        self.assertEqual(str_find("abcabc", "c"), 2)
        self.assertEqual(str_find("abcabc", "d"), -1)

    def test_str_rfind(self):
        # Note: inputs are Unicode strings.
        self.assertEqual(str_rfind("abcabc", "c"), 5)
        self.assertEqual(str_rfind("abcabc", "d"), -1)

    if six.PY2:
        def test_str_find_with_bytestrings(self):
            # Try all possible mixes of Unicode with bytes.
            self.assertEqual(str_find("abcabc", "b"), 1)
            self.assertEqual(str_find(u"abcabc", "b"), 1)
            self.assertEqual(str_find("abcabc", u"b"), 1)
            self.assertEqual(str_find(u"abcabc", u"b"), 1)

        def test_str_rfind_with_bytestrings(self):
            # Try all possible mixes of Unicode with bytes.
            self.assertEqual(str_rfind("abcabc", "b"), 4)
            self.assertEqual(str_rfind(u"abcabc", "b"), 4)
            self.assertEqual(str_rfind("abcabc", u"b"), 4)
            self.assertEqual(str_rfind(u"abcabc", u"b"), 4)
