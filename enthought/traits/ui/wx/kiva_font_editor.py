#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# 
# Author: David C. Morrill
# Date: 12/22/2004
#
#  Symbols defined: ToolkitEditorFactory
#                   KivaFont
#
#------------------------------------------------------------------------------
""" Defines the font editor factory for Kiva fonts, for the wxPython user 
interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.trait_base \
    import SequenceTypes
    
from enthought.traits.ui.wx.font_editor \
    import ToolkitEditorFactory as EditorFactory
     
#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# All available typeface names for fonts
facenames = None

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for Kiva fonts.
    """
    
    #---------------------------------------------------------------------------
    #  Returns a Font's 'face name':
    #---------------------------------------------------------------------------
    
    def face_name ( self, font ):
        """ Returns a Font's typeface name.
        """
        face_name = font.face_name
        if type( face_name ) in SequenceTypes:
            face_name = face_name[0]
            
        return face_name

    #---------------------------------------------------------------------------
    #  Returns a wxFont object corresponding to a specified object's font trait:
    #---------------------------------------------------------------------------
    
    def to_wx_font ( self, editor ):
        """ Returns a wxFont object corresponding to a specified object's font
            trait.
        """
        import enthought.kiva.constants as kc
        
        font   = editor.value
        weight = ( wx.NORMAL, wx.BOLD   )[ font.weight == kc.BOLD ]
        style  = ( wx.NORMAL, wx.ITALIC )[ font.style  == kc.ITALIC ]
        family = { kc.DEFAULT:    wx.DEFAULT,
                   kc.DECORATIVE: wx.DECORATIVE,
                   kc.ROMAN:      wx.ROMAN,
                   kc.SCRIPT:     wx.SCRIPT,
                   kc.SWISS:      wx.SWISS,
                   kc.MODERN:     wx.MODERN }.get( font.family, wx.SWISS )
                   
        return wx.Font( font.size, family, style, weight,
                        (font.underline != 0), self.face_name( font ) )
 
    #---------------------------------------------------------------------------
    #  Gets the application equivalent of a wxPython value:
    #---------------------------------------------------------------------------
    
    def from_wx_font ( self, font ):
        """ Gets the application equivalent of a wxPython value.
        """
        import enthought.kiva.constants as kc
        from enthought.kiva.fonttools import Font
        
        return Font( font.GetPointSize(), 
                     { wx.DEFAULT:    kc.DEFAULT,
                       wx.DECORATIVE: kc.DECORATIVE,
                       wx.ROMAN:      kc.ROMAN,
                       wx.SCRIPT:     kc.SCRIPT,
                       wx.SWISS:      kc.SWISS,
                       wx.MODERN:     kc.MODERN }.get( font.GetFamily(), 
                                                       kc.SWISS ),
                    ( kc.NORMAL, kc.BOLD   )[ font.GetWeight() == wx.BOLD ],
                    ( kc.NORMAL, kc.ITALIC )[ font.GetStyle()  == wx.ITALIC ],
                    font.GetUnderlined() - 0, #convert Bool to an int type
                    font.GetFaceName() )   

    #---------------------------------------------------------------------------
    #  Returns the text representation of the specified object trait value:
    #---------------------------------------------------------------------------
    
    def str_font ( self, font ):
        """ Returns the text representation of the specified object trait value.
        """
        import enthought.kiva.constants as kc
        
        weight    = { kc.BOLD:   ' Bold'   }.get( font.weight, '' )
        style     = { kc.ITALIC: ' Italic' }.get( font.style,  '' )
        underline = [ '', ' Underline' ][ font.underline != 0 ]
        
        return '%s point %s%s%s%s' % (
               font.size, self.face_name( font ), style, weight, underline )

    #---------------------------------------------------------------------------
    #  Returns a list of all available font facenames:
    #---------------------------------------------------------------------------
    
    def all_facenames ( self ):
        """ Returns a list of all available font typeface names.
        """
        global facenames
        
        if facenames is None:
           from enthought.freetype import font_lookup 
           
           facenames = font_lookup.default_font_info.names()              
           if facenames[0] == '':
               del facenames[0]
               
           facenames.sort()
           
        return facenames

