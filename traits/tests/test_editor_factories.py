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

from traits.traits import (
    BytesEditors,
    MultilineTextEditors,
    bytes_editor,
    multi_line_text_editor,
)
from traits.testing.optional_dependencies import requires_traitsui, traitsui

@requires_traitsui
class TestDefaultEditors(unittest.TestCase):

    def tearDown(self):
        BytesEditors.clear()

    def test_bytes_editor_default(self):
        editor = bytes_editor()

        self.assertIsInstance(editor, traitsui.api.TextEditor)
        self.assertTrue(editor.auto_set)
        self.assertFalse(editor.enter_set)

        # test formatter
        formatted = editor.format_func(b'\xde\xad\xbe\xef')
        self.assertEqual(formatted, "deadbeef")

        # test evaluator
        evaluated = editor.evaluate("deadbeef")
        self.assertEqual(evaluated, b'\xde\xad\xbe\xef')

    def test_bytes_editor_options(self):
        editor = bytes_editor(auto_set=False, enter_set=True, encoding='ascii')

        self.assertIsInstance(editor, traitsui.api.TextEditor)
        self.assertFalse(editor.auto_set)
        self.assertTrue(editor.enter_set)

        # test formatter
        formatted = editor.format_func(b"deadbeef")
        self.assertEqual(formatted, "deadbeef")

        # test evaluator
        evaluated = editor.evaluate("deadbeef")
        self.assertEqual(evaluated, b"deadbeef")

    def test_bytes_editor_caching(self):
        editor_1 = bytes_editor()
        editor_2 = bytes_editor()

        self.assertIs(editor_1, editor_2)

        editor_3 = bytes_editor(auto_set=False, enter_set=True, encoding='ascii')
        editor_4 = bytes_editor(auto_set=False, enter_set=True, encoding='ascii')

        self.assertIs(editor_3, editor_4)


@requires_traitsui
class TestMultiLineEditor(unittest.TestCase):

    def tearDown(self):
        MultilineTextEditors.clear()

    def test_multi_line_text_editor_default(self):
        editor = multi_line_text_editor()

        self.assertIsInstance(editor, traitsui.api.TextEditor)
        self.assertTrue(editor.multi_line)
        self.assertTrue(editor.auto_set)
        self.assertFalse(editor.enter_set)

    def test_multi_line_text_editor_options(self):
        editor = multi_line_text_editor(auto_set=False, enter_set=True)

        self.assertIsInstance(editor, traitsui.api.TextEditor)
        self.assertTrue(editor.multi_line)
        self.assertFalse(editor.auto_set)
        self.assertTrue(editor.enter_set)

    def test_multi_line_text_editor_caching(self):
        editor_1 = multi_line_text_editor()
        editor_2 = multi_line_text_editor()

        self.assertIs(editor_1, editor_2)

        editor_3 = multi_line_text_editor(auto_set=False, enter_set=True)
        editor_4 = multi_line_text_editor(auto_set=False, enter_set=True)

        self.assertIs(editor_3, editor_4)
