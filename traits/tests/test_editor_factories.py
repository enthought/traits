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
Tests for Editor factories.

"""

import datetime
import unittest

from traits.has_traits import HasTraits
from traits.trait_types import Instance, List, Str
from traits.editor_factories import (
    _datetime_to_datetime_str,
    _datetime_str_to_datetime,
    bytes_editor,
    multi_line_text_editor,
    list_editor,
    password_editor,
)
from traits.testing.optional_dependencies import requires_traitsui, traitsui


class SimpleEditorTestMixin:

    def setUp(self):
        import traits.editor_factories
        self.factory = getattr(traits.editor_factories, self.factory_name)
        self.traitsui_factory = getattr(traitsui.api, self.traitsui_name)

    def test_editor(self):
        editor = self.factory()

        if isinstance(self.traitsui_factory, traitsui.api.BasicEditorFactory):
            self.assertIsInstance(editor, traitsui.api.BasicEditorFactory)
        else:
            self.assertIsInstance(editor, self.traitsui_factory)


@requires_traitsui
class TestDateEditor(SimpleEditorTestMixin, unittest.TestCase):
    traitsui_name = "DateEditor"
    factory_name = "date_editor"


@requires_traitsui
class TestDatetimeEditor(SimpleEditorTestMixin, unittest.TestCase):
    traitsui_name = "DatetimeEditor"
    factory_name = "datetime_editor"

    def test_str_to_obj_conversions(self):
        # Roundtrip None -> str -> None
        obj = None
        obj_str = _datetime_to_datetime_str(obj)
        self.assertEqual(obj_str, "")
        self.assertEqual(_datetime_str_to_datetime(obj_str), obj)

        # Roundtrip datetime -> str -> datetime
        obj = datetime.datetime(2019, 1, 13)
        obj_str = _datetime_to_datetime_str(obj)
        self.assertIsInstance(obj_str, str)
        self.assertEqual(_datetime_str_to_datetime(obj_str), obj)

        # Roundtrip valid_str -> datetime -> valid_str
        obj_str = "2020-02-15T11:12:13"
        obj = _datetime_str_to_datetime(obj_str)
        self.assertIsInstance(obj, datetime.datetime)
        self.assertEqual(_datetime_to_datetime_str(obj), obj_str)

        # Roundtrip "" -> None -> ""
        obj_str = ""
        obj = _datetime_str_to_datetime(obj_str)
        self.assertIsNone(obj)
        self.assertEqual(_datetime_to_datetime_str(obj), obj_str)


@requires_traitsui
class TestCodeEditor(SimpleEditorTestMixin, unittest.TestCase):
    traitsui_name = "CodeEditor"
    factory_name = "code_editor"


@requires_traitsui
class TestHTMLEditor(SimpleEditorTestMixin, unittest.TestCase):
    traitsui_name = "HTMLEditor"
    factory_name = "html_editor"


@requires_traitsui
class TestShellEditor(SimpleEditorTestMixin, unittest.TestCase):
    traitsui_name = "ShellEditor"
    factory_name = "shell_editor"


@requires_traitsui
class TestTimeEditor(SimpleEditorTestMixin, unittest.TestCase):
    traitsui_name = "TimeEditor"
    factory_name = "time_editor"


@requires_traitsui
class TestBytesEditor(unittest.TestCase):

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


@requires_traitsui
class TestMultiLineEditor(unittest.TestCase):

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


@requires_traitsui
class TestPasswordEditor(unittest.TestCase):

    def test_password_editor_default(self):
        editor = password_editor()

        self.assertIsInstance(editor, traitsui.api.TextEditor)
        self.assertTrue(editor.password)
        self.assertTrue(editor.auto_set)
        self.assertFalse(editor.enter_set)

    def test_password_editor_options(self):
        editor = password_editor(auto_set=False, enter_set=True)

        self.assertIsInstance(editor, traitsui.api.TextEditor)
        self.assertTrue(editor.password)
        self.assertFalse(editor.auto_set)
        self.assertTrue(editor.enter_set)


@requires_traitsui
class TestListEditor(unittest.TestCase):

    def test_list_editor_default(self):
        trait = List(Str)
        editor = list_editor(trait, trait)

        self.assertIsInstance(editor, traitsui.api.ListEditor)
        self.assertEqual(editor.trait_handler, trait)
        self.assertEqual(editor.rows, 5)
        self.assertFalse(editor.use_notebook)
        self.assertEqual(editor.page_name, '')

    def test_list_editor_options(self):
        trait = List(Str, rows=10, use_notebook=True, page_name='page')
        editor = list_editor(trait, trait)

        self.assertIsInstance(editor, traitsui.api.ListEditor)
        self.assertEqual(editor.trait_handler, trait)
        self.assertEqual(editor.rows, 10)
        self.assertTrue(editor.use_notebook)
        self.assertEqual(editor.page_name, 'page')

    def test_list_editor_list_instance(self):
        trait = List(Instance(HasTraits))
        editor = list_editor(trait, trait)
        self.assertIsInstance(editor, traitsui.api.TableEditor)
