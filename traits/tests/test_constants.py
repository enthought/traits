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

from traits.api import ComparisonMode


class TestConstants(unittest.TestCase):
    def test_deprecated_comparison_constants(self):
        # Check availability of comparison constants.
        from traits.api import (
            NO_COMPARE, OBJECT_IDENTITY_COMPARE, RICH_COMPARE)
        self.assertIs(NO_COMPARE, ComparisonMode.none)
        self.assertIs(
            OBJECT_IDENTITY_COMPARE, ComparisonMode.identity)
        self.assertIs(
            RICH_COMPARE, ComparisonMode.equality)
