
from __future__ import absolute_import

from nose.tools import assert_equals

from ...api import DefaultOverride, EditorFactory
from ....api import HasTraits, Int


class DummyEditor(EditorFactory):

    x = Int(10)
    y = Int(20)

    def simple_editor(self, ui, object, name, description, parent):
        return ('simple_editor', self, ui, object, name, description, parent)

    def custom_editor(self, ui, object, name, description, parent):
        return ('custom_editor', self, ui, object, name, description, parent)

    def text_editor(self, ui, object, name, description, parent):
        return ('text_editor', self, ui, object, name, description, parent)

    def readonly_editor(self, ui, object, name, description, parent):
        return ('readonly_editor', self, ui, object, name, description, parent)


class NewInt(Int):
    def create_editor(self):
        return DummyEditor()


class Dummy(HasTraits):
    x = NewInt()

object = Dummy()
do = DefaultOverride(x=15, y=25, format_str='%r')

def test_simple_override():
    editor_name, editor, ui, obj, name, description, parent = do.simple_editor('ui', object, 'x', 'description', 'parent')
    assert_equals(editor_name, 'simple_editor')
    assert_equals(editor.x, 15)
    assert_equals(editor.y, 25)
    assert_equals(obj, object)
    assert_equals(name, 'x')
    assert_equals(description, 'description')
    assert_equals(parent, 'parent')

def test_text_override():
    editor_name, editor, ui, obj, name, description, parent = do.text_editor('ui', object, 'x', 'description', 'parent')
    assert_equals(editor_name, 'text_editor')
    assert_equals(editor.x, 15)
    assert_equals(editor.y, 25)
    assert_equals(obj, object)
    assert_equals(name, 'x')
    assert_equals(description, 'description')
    assert_equals(parent, 'parent')

def test_custom_override():
    editor_name, editor, ui, obj, name, description, parent = do.custom_editor('ui', object, 'x', 'description', 'parent')
    assert_equals(editor_name, 'custom_editor')
    assert_equals(editor.x, 15)
    assert_equals(editor.y, 25)
    assert_equals(obj, object)
    assert_equals(name, 'x')
    assert_equals(description, 'description')
    assert_equals(parent, 'parent')

def test_readonly_override():
    editor_name, editor, ui, obj, name, description, parent = do.readonly_editor('ui', object, 'x', 'description', 'parent')
    assert_equals(editor_name, 'readonly_editor')
    assert_equals(editor.x, 15)
    assert_equals(editor.y, 25)
    assert_equals(obj, object)
    assert_equals(name, 'x')
    assert_equals(description, 'description')
    assert_equals(parent, 'parent')
