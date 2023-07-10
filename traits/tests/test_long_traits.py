# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
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
    BaseCInt,
    BaseCLong,
    BaseInt,
    BaseLong,
    CInt,
    CLong,
    Int,
    Long,
)


class TestLong(unittest.TestCase):
    def test_aliases(self):
        self.assertIs(BaseLong, BaseInt)
        self.assertIs(Long, Int)
        self.assertIs(BaseCLong, BaseCInt)
        self.assertIs(CLong, CInt)
