"""
Editor factory that overrides certain attributes of the default editor.

For example, the default editor for Range(low=0, high=1500) has
'1500' as the upper label.  To change it to 'Max' instead, use

my_range = Range(low=0, high=1500,
                 editor=DefaultOverride(high_label='Max'))

Alternatively, the override can also be specified in the view:

View(Item('my_range', editor=DefaultOverride(high_label='Max'))

"""

from __future__ import absolute_import

from ...api import Dict
from ..editor_factory import EditorFactory

class DefaultOverride(EditorFactory):
    """Editor factory for selectively overriding certain parameters
    of the default editor.

    """
    _overrides = Dict

    def __init__(self, *args, **overrides):
        EditorFactory.__init__(self, *args)
        self._overrides = overrides

    def _customise_default(self, editor_kind, ui, object, name,
                           description, parent):
        """
        Obtain the given trait's default editor and set the parameters
        specified in `overrides` above.
        """
        trait = object.trait(name)
        editor_factory = trait.trait_type.create_editor()
        for option in self._overrides:
            setattr(editor_factory, option, self._overrides[option])

        editor = getattr(editor_factory, editor_kind)(ui, object, name,
                                                      description, parent)
        return editor

    def simple_editor(self, ui, object, name, description, parent):
        return self._customise_default('simple_editor', ui, object,
                                       name, description, parent)

    def custom_editor(self, ui, object, name, description, parent):
        return self._customise_default('custom_editor', ui, object,
                                       name, description, parent)

    def text_editor(self, ui, object, name, description, parent):
        return self._customise_default('text_editor', ui, object,
                                       name, description, parent)

    def readonly_editor(self, ui, object, name, description, parent):
        return self._customise_default('readonly_editor', ui, object,
                                       name, description, parent)
