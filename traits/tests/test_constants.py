
#  Copyright (c) 2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!

import unittest

from traits.api import ComparisonMode


class TestConstants(unittest.TestCase):
    def test_deprecated_comparison_constants(self):
        # Check availability of comparison constants.
        from traits.api import (
            NO_COMPARE, OBJECT_IDENTITY_COMPARE, RICH_COMPARE)
        self.assertIs(NO_COMPARE, ComparisonMode.no_compare)
        self.assertIs(
            OBJECT_IDENTITY_COMPARE, ComparisonMode.object_id_compare)
        self.assertIs(
            RICH_COMPARE, ComparisonMode.equality_compare)
