# ------------------------------------------------------------------------------
#
#  Copyright (c) 2017, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
# ------------------------------------------------------------------------------
"""
Tests for Editor factories.

"""

import unittest

from traits.traits import multi_line_text_editor
from traits.testing.optional_dependencies import requires_traitsui


@requires_traitsui
class TestMultiLineEditor(unittest.TestCase):
    def test_auto_set_default(self):
        a = multi_line_text_editor(auto_set=False)
        self.assertFalse(a.auto_set)
        b = multi_line_text_editor()
        self.assertTrue(b.auto_set)

    def test_enter_set_default(self):
        a = multi_line_text_editor(enter_set=True)
        self.assertTrue(a.enter_set)
        b = multi_line_text_editor()
        self.assertFalse(b.enter_set)
