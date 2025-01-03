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

from traits.api import (
    BaseCStr,
    BaseCUnicode,
    BaseStr,
    BaseUnicode,
    CStr,
    CUnicode,
    Str,
    Unicode,
)


class TestUnicodeTraits(unittest.TestCase):
    def test_aliases(self):
        self.assertIs(Unicode, Str)
        self.assertIs(CUnicode, CStr)
        self.assertIs(BaseUnicode, BaseStr)
        self.assertIs(BaseCUnicode, BaseCStr)
