# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
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

import unittest

from traits.has_traits import HasTraits
from traits.trait_types import Instance, List, Str
from traits.editor_factories import (
    BytesEditors,
    MultilineTextEditors,
    PasswordEditors,
    bytes_editor,
    multi_line_text_editor,
    list_editor,
    password_editor,
)
from traits.testing.optional_dependencies import requires_traitsui, traitsui


# The DatetimeEditor is not yet in a released version of TraitsUI. It
# will be available in TraitsUI >= 6.2.0.
try:
    DatetimeEditor = traitsui.api.DatetimeEditor
except AttributeError:
    DatetimeEditor = None


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


class SimpleEditorWithCachingTestMixin(SimpleEditorTestMixin):

    def tearDown(self):
        import traits.editor_factories
        setattr(traits.editor_factories, self.cache_name, None)

    def test_editor_caching(self):
        editor_1 = self.factory()
        editor_2 = self.factory()

        self.assertIs(editor_1, editor_2)


@requires_traitsui
class TestDateEditor(SimpleEditorWithCachingTestMixin, unittest.TestCase):
    cache_name = "DateEditor"
    traitsui_name = "DateEditor"
    factory_name = "date_editor"


@unittest.skipIf(DatetimeEditor is None, "DatetimeEditor not available")
class TestDatetimeEditor(SimpleEditorTestMixin, unittest.TestCase):
    traitsui_name = "DatetimeEditor"
    factory_name = "datetime_editor"


@requires_traitsui
class TestCodeEditor(SimpleEditorWithCachingTestMixin, unittest.TestCase):
    cache_name = "SourceCodeEditor"
    traitsui_name = "CodeEditor"
    factory_name = "code_editor"


@requires_traitsui
class TestHTMLEditor(SimpleEditorWithCachingTestMixin, unittest.TestCase):
    cache_name = "HTMLTextEditor"
    traitsui_name = "HTMLEditor"
    factory_name = "html_editor"


@requires_traitsui
class TestShellEditor(SimpleEditorWithCachingTestMixin, unittest.TestCase):
    cache_name = "PythonShellEditor"
    traitsui_name = "ShellEditor"
    factory_name = "shell_editor"


@requires_traitsui
class TestTimeEditor(SimpleEditorWithCachingTestMixin, unittest.TestCase):
    cache_name = "TimeEditor"
    traitsui_name = "TimeEditor"
    factory_name = "time_editor"


@requires_traitsui
class TestBytesEditor(unittest.TestCase):

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

        editor_3 = bytes_editor(
            auto_set=False, enter_set=True, encoding='ascii'
        )
        editor_4 = bytes_editor(
            auto_set=False, enter_set=True, encoding='ascii'
        )

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


@requires_traitsui
class TestPasswordEditor(unittest.TestCase):

    def tearDown(self):
        PasswordEditors.clear()

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

    def test_password_editor_caching(self):
        editor_1 = password_editor()
        editor_2 = password_editor()

        self.assertIs(editor_1, editor_2)

        editor_3 = password_editor(auto_set=False, enter_set=True)
        editor_4 = password_editor(auto_set=False, enter_set=True)

        self.assertIs(editor_3, editor_4)


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
