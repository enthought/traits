# reuse_editor.py --- Example of reusing a trait editor
from enthought.traits.api import HasTraits, Trait
import enthought.traits.ui
from enthought.traits.ui.api import ColorEditor
from wxPython import wx

color_editor = ColorEditor()

class Polygon(HasTraits):
    line_color = Trait(wx.wxColour(0, 0, 0),
                       editor=color_editor)
    fill_color = Trait(wx.wxColour(255, 255, 255),
                       editor=color_editor)
