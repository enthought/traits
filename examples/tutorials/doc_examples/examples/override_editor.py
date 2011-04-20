#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# override_editor.py --- Example of overriding a trait
#                        editor
from traits.api import HasTraits, Trait
import traitsui
from traitsui.api import ColorEditor
from wxPython import wx

class Polygon(HasTraits):
    line_color = Trait(wx.wxColour(0, 0, 0),
                       editor=ColorEditor())
