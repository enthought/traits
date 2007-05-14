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
# Date: 10/21/2004
#
#  Symbols defined: ToolkitEditorFactory
#
#------------------------------------------------------------------------------
""" Defines the various range editors and the range editor factory, for the 
wxPython user interface toolkit.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys
import wx

from math \
    import log10
    
from enthought.traits.api \
     import CTrait, TraitError, Property, Range, Enum, Str, Int, Float, Any, \
            true, false

from enthought.traits.ui.api \
    import View
    
from editor_factory \
    import EditorFactory, TextEditor
    
from editor \
    import Editor
    
from constants \
    import OKColor, ErrorColor

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for range editors.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Number of columns when displayed as an enumeration
    cols = Range( 1, 20 )
    
    # Is user input set on every keystroke?
    auto_set = true
    
    # Is user input set when the Enter key is pressed?
    enter_set = false
    
    # Label for the low end of the range
    low_label = Str
    
    # Label for the high end of the range
    high_label = Str
    
    # The width of the low and high labels
    label_width = Int
    
    # The name of an [object.]trait that defines the low value for the range
    low_name = Str
    
    # The name of an [object.]trait that defines the high value for the range
    high_name = Str
    
    # Formatting string used to format value and labels
    format = Str( '%s' )
    
    # Is the range for floating pointer numbers (vs. integers)?
    is_float = true
    
    # Low end of range
    low = Property
    
    # High end of range
    high = Property
    
    # Display mode to use
    mode = Enum( 'auto', 'slider', 'xslider', 'spinner', 'enum', 'text' )
    
    #---------------------------------------------------------------------------
    #  Traits view definition:    
    #---------------------------------------------------------------------------
        
    traits_view = View( [ [ 'low', 'high',
                            '|[Range]' ],
                          [ 'low_label{Low}', 'high_label{High}', 
                            '|[Range Labels]' ],
                          [ 'auto_set{Set automatically}', 
                            'enter_set{Set on enter key pressed}',
                            'is_float{Is floating point range}',
                            '-[Options]>' ],
                          [ 'cols', 
                            '|[Number of columns for integer custom style]<>' ]
                        ] )
        
    #---------------------------------------------------------------------------
    #  Performs any initialization needed after all constructor traits have 
    #  been set:
    #---------------------------------------------------------------------------
     
    def init ( self, handler = None ):
        """ Performs any initialization needed after all constructor traits 
            have been set.
        """
        if handler is not None:
            if isinstance( handler, CTrait ):
                handler = handler.handler
            self.low  = handler._low
            self.high = handler._high
        else:
            if self.low is None:
                self.low  = 0.0
            if self.high is None:
                self.high = 1.0
            
    #---------------------------------------------------------------------------
    #  Define the 'low' and 'high' traits:
    #---------------------------------------------------------------------------
            
    def _get_low ( self ):
        return self._low
        
    def _set_low ( self, low ):
        old_low         = self._low
        self._low = low = self._cast( low )
        self.is_float   = (type( low ) is float)
        if (self.low_label == '') or (self.low_label == str( old_low )):
            self.low_label = str( low  )
            
    def _get_high ( self ):
        return self._high
        
    def _set_high ( self, high ):
        old_high          = self._high
        self._high = high = self._cast( high )
        self.is_float     = (type( high ) is float)
        if (self.high_label == '') or (self.high_label == str( old_high )):
            self.high_label = str( high )
            
    def _cast ( self, value ):
        if type( value ) is not str:
            return value
        try:
            return int( value )
        except:
            return float( value )
    
    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------
    
    def simple_editor ( self, ui, object, name, description, parent ):
        """ Creates a simple style of editor.
        
        The type of editor depends on the type and extent of the range being
        edited:
            
        * One end of range is unspecified: RangeTextEditor
        * **mode** is specified and not 'auto': editor corresponding to **mode**
        * Floating point range with extent > 100: LargeRangeSliderEditor
        * Integer range or floating point range with extent <= 100: 
          SimpleSliderEditor
        * All other cases: SimpleSpinEditor
        """
        if (self.low is None) or (self.high is None):
            return RangeTextEditor( parent,
                                    factory     = self, 
                                    ui          = ui, 
                                    object      = object, 
                                    name        = name, 
                                    description = description )
                                    
        if self.mode != 'auto':
            return SimpleEditorMap[ self.mode ]( parent, 
                                                 factory     = self, 
                                                 ui          = ui, 
                                                 object      = object, 
                                                 name        = name, 
                                                 description = description )
                                           
        if self.is_float and (abs( self.high - self.low ) > 100):
            return LargeRangeSliderEditor( parent,
                                       factory     = self, 
                                       ui          = ui, 
                                       object      = object, 
                                       name        = name, 
                                       description = description )
            
        if self.is_float or (abs( self.high - self.low ) <= 100):
            return SimpleSliderEditor( parent,
                                       factory     = self, 
                                       ui          = ui, 
                                       object      = object, 
                                       name        = name, 
                                       description = description )
        return SimpleSpinEditor( parent,
                                 factory     = self, 
                                 ui          = ui, 
                                 object      = object, 
                                 name        = name, 
                                 description = description ) 
    
    def custom_editor ( self, ui, object, name, description, parent ):
        """ Creates a custom style of range editor
        
        The type of editor depends on the type and extent of the range being
        edited:
            
        * One end of range is unspecified: RangeTextEditor
        * **mode** is specified and not 'auto': editor corresponding to **mode**
        * Floating point range: Same as "simple" style
        * Integer range with extent > 15: Same as "simple" style
        * Integer range with extent <= 15: CustomEnumEditor

        """
        if (self.low is None) or (self.high is None):
            return RangeTextEditor( parent,
                                    factory     = self, 
                                    ui          = ui, 
                                    object      = object, 
                                    name        = name, 
                                    description = description )
                                    
        if self.mode != 'auto':
            return CustomEditorMap[ self.mode ]( parent, 
                                                 factory     = self, 
                                                 ui          = ui, 
                                                 object      = object, 
                                                 name        = name, 
                                                 description = description )
                                                 
        if self.is_float or (abs( self.high - self.low ) > 15):
           return self.simple_editor( ui, object, name, description, parent )
           
        return CustomEnumEditor( parent, self, ui, object, name, description )
    
    def text_editor ( self, ui, object, name, description, parent ):
        """ Creates a text style of range editor.
        """
        return RangeTextEditor( parent,
                                factory     = self, 
                                ui          = ui, 
                                object      = object, 
                                name        = name, 
                                description = description ) 
                                      
#-------------------------------------------------------------------------------
#  'SimpleSliderEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleSliderEditor ( Editor ):
    """ Simple style of range editor that displays a slider and a text field. 
    
    The user can set a value either by moving the slider or by typing a value 
    in the text field.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------

    # Low value for the slider range
    low = Any
    
    # High value for the slider range
    high = Any
    
    # Formatting string used to format value and labels
    format = Str
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        if not factory.low_name:
            self.low = factory.low
            
        if not factory.high_name:
            self.high = factory.high
            
        self.format = factory.format
        size        = wx.DefaultSize
        
        if factory.label_width > 0:
            size = wx.Size( factory.label_width, 20 )
            
        self.sync_value( factory.low_name,  'low',  'from' )
        self.sync_value( factory.high_name, 'high', 'from' )
        low  = self.low
        high = self.high
        self.control = panel = wx.Panel( parent, -1 )
        sizer  = wx.BoxSizer( wx.HORIZONTAL )
        fvalue = self.value
        
        try:
            fvalue_text = self.format % fvalue
            1 / (low <= fvalue <= high)
        except:
            fvalue_text = ''
            fvalue      = low
        if high > low:
            ivalue = int( (float( fvalue - low ) / (high - low)) * 10000 )
        else:
            ivalue = low
            
        self._label_lo = wx.StaticText( panel, -1, '999999', size = size,
                                style = wx.ALIGN_RIGHT | wx.ST_NO_AUTORESIZE )
        sizer.Add( self._label_lo, 0, wx.ALIGN_CENTER )
        panel.slider = slider = wx.Slider( panel, -1, ivalue, 0, 10000,
                                   size   = wx.Size( 80, 20 ),
                                   style  = wx.SL_HORIZONTAL | wx.SL_AUTOTICKS )
        slider.SetTickFreq( 1000, 1 )
        slider.SetPageSize( 1000 )
        slider.SetLineSize( 100 )
        wx.EVT_SCROLL( slider, self.update_object_on_scroll )
        sizer.Add( slider, 1, wx.EXPAND )
        self._label_hi = wx.StaticText( panel, -1, '999999', size = size )
        sizer.Add( self._label_hi, 0, wx.ALIGN_CENTER )
        
        if factory.enter_set:
            panel.text = text = wx.TextCtrl( panel, -1, fvalue_text,
                                             size  = wx.Size( 56, 20 ),
                                             style = wx.TE_PROCESS_ENTER )
            wx.EVT_TEXT_ENTER( panel, text.GetId(), 
                               self.update_object_on_enter )
        else:                                               
            panel.text = text = wx.TextCtrl( panel, -1, fvalue_text,
                                             size  = wx.Size( 56, 20 ) )
                                             
        wx.EVT_KILL_FOCUS( text, self.update_object_on_enter )
        sizer.Add( text, 0, wx.LEFT | wx.EXPAND, 4 )
        
        low_label = factory.low_label
        if factory.low_name != '':
            low_label = self.format % self.low
            
        high_label = factory.high_label
        if factory.high_name != '':
            high_label = self.format % self.high
            
        self._label_lo.SetLabel( low_label )
        self._label_hi.SetLabel( high_label )
        self.set_tooltip( slider )
        self.set_tooltip( self._label_lo )
        self.set_tooltip( self._label_hi )
        self.set_tooltip( text )
        
        # Set-up the layout:
        panel.SetSizerAndFit( sizer )
       
    #---------------------------------------------------------------------------
    #  Handles the user changing the current slider value: 
    #---------------------------------------------------------------------------
    
    def update_object_on_scroll ( self, event ):
        """ Handles the user changing the current slider value.
        """
        value = self.low + ((float( event.GetPosition() ) / 10000.0) * 
                            (self.high - self.low))
        if not self.factory.is_float:
            value = int( value )
        self.control.text.SetValue( self.format % value )
        event_type = event.GetEventType()
        if ((event_type == wx.wxEVT_SCROLL_ENDSCROLL) or
            (self.factory.auto_set and 
             (event_type == wx.wxEVT_SCROLL_THUMBTRACK))):
            self.value = value

    #---------------------------------------------------------------------------
    #  Handle the user pressing the 'Enter' key in the edit control:
    #---------------------------------------------------------------------------
 
    def update_object_on_enter ( self, event ):
        """ Handles the user pressing the Enter key in the text field.
        """
        try:
            try:
                value = eval( self.control.text.GetValue().strip() )
            except Exception, ex:
                # The entered something that didn't eval as a number, (e.g., 'foo')
                # pretend it didn't happen
                value = self.value
                self.control.text.SetValue(str(value))
            if not self.factory.is_float:
                value = int( value )
            self.value = value 
            self.control.slider.SetValue( 
                int( ((float( value ) - self.low) / 
                     (self.high - self.low)) * 10000 ) )
        except TraitError, excp:
            pass
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        value = self.value
        low   = self.low
        high  = self.high
        try:
            text = self.format % value
            1 / (low <= value <= high)
        except:
            text  = ''
            value = low
        if high > low:
            ivalue = int( (float( value - low ) / (high - low)) * 10000.0 )
        else:
            ivalue = low
        self.control.text.SetValue( text )
        self.control.slider.SetValue( ivalue )
        
    #---------------------------------------------------------------------------
    #  Handles the 'low'/'high' traits being changed:  
    #---------------------------------------------------------------------------

    def _low_changed ( self, low ):
        if self.value < low:
            if self.factory.is_float:
                self.value = float( low )
            else:
                self.value = int( low )
                
        if self._label_lo is not None:
            self._label_lo.SetLabel( self.format % low  )
            self.update_editor()
            
    def _high_changed ( self, high ):
        if self.value > high:
            if self.factory.is_float:
                self.value = float( high )
            else:
                self.value = int( high )
        if self._label_hi is not None:
            self._label_hi.SetLabel( self.format % high  )
            self.update_editor()

#-------------------------------------------------------------------------------
#  'LargeRangeSliderEditor' class:
#-------------------------------------------------------------------------------
                               
class LargeRangeSliderEditor ( Editor ):
    """ A slider editor for large ranges. 
    
    The editor displays a slider and a text field. A subset of the total range
    is displayed in the slider; arrow buttons at each end of the slider let
    the user move the displayed range higher or lower.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # Low value for the slider range
    low = Any(0)
    
    # High value for the slider range
    high = Any(1)
    
    # Low end of displayed range
    cur_low = Float
    
    # High end of displayed range
    cur_high = Float
    
    # Flag indicating that the UI is in the process of being updated
    ui_changing = false

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """        
        factory = self.factory
        if not factory.low_name:
            self.set( low = factory.low, trait_change_notify = False )
        if not factory.high_name:
            self.set( high = factory.high, trait_change_notify = False )
        self.init_range()
        low  = self.cur_low
        high = self.cur_high

        self._set_format()
        self.control = panel = wx.Panel( parent, -1 )
        sizer  = wx.BoxSizer( wx.HORIZONTAL )
        fvalue = self.value
        try:
            fvalue_text = self._format % fvalue
            1 / (factory.low <= fvalue <= factory.high)
        except:
            fvalue_text = ''
            fvalue      = factory.low
        ivalue = int( (float( fvalue - low ) / (high - low)) * 10000 )
        
        # Lower limit label:
        label_lo       = wx.StaticText( panel, -1, '999999' )
        panel.label_lo = label_lo
        sizer.Add( label_lo, 2, wx.ALIGN_CENTER )
        
        # Lower limit button:
        bmp       = wx.ArtProvider.GetBitmap( wx.ART_GO_BACK, 
                                              size = ( 15, 15 ) )
        button_lo = wx.BitmapButton( panel, -1, bitmap = bmp, size = ( -1, 20 ),
                                     style = wx.BU_EXACTFIT | wx.NO_BORDER )
        panel.button_lo = button_lo
        button_lo.Bind( wx.EVT_BUTTON, self.reduce_range, button_lo )
        sizer.Add( button_lo, 1, wx.ALIGN_CENTER )
        
        # Slider:        
        panel.slider = slider = wx.Slider( panel, -1, ivalue, 0, 10000,
                                   size   = wx.Size( 80, 20 ),
                                   style  = wx.SL_HORIZONTAL | wx.SL_AUTOTICKS )
        slider.SetTickFreq( 1000, 1 )
        slider.SetPageSize( 1000 )
        slider.SetLineSize( 100 )
        wx.EVT_SCROLL( slider, self.update_object_on_scroll )
        sizer.Add( slider, 6, wx.EXPAND )
        
        # Upper limit button:
        bmp       = wx.ArtProvider.GetBitmap( wx.ART_GO_FORWARD,
                                              size = ( 15, 15 ) )
        button_hi = wx.BitmapButton( panel, -1, bitmap = bmp, size = ( -1, 20 ),
                                     style = wx.BU_EXACTFIT | wx.NO_BORDER )
        panel.button_hi = button_hi
        button_hi.Bind( wx.EVT_BUTTON, self.increase_range, button_hi )
        sizer.Add( button_hi, 1, wx.ALIGN_CENTER )
        
        # Upper limit label:
        label_hi = wx.StaticText( panel, -1, '999999' )
        panel.label_hi = label_hi
        sizer.Add( label_hi, 2, wx.ALIGN_CENTER )
        
        # Text entry:
        if factory.enter_set:
            panel.text = text = wx.TextCtrl( panel, -1, fvalue_text,
                                             size  = wx.Size( 56, 20 ),
                                             style = wx.TE_PROCESS_ENTER )
            wx.EVT_TEXT_ENTER( panel, text.GetId(), 
                               self.update_object_on_enter )
        else:                                               
            panel.text = text = wx.TextCtrl( panel, -1, fvalue_text,
                                             size  = wx.Size( 56, 20 ) )
        wx.EVT_KILL_FOCUS( text, self.update_object_on_enter )
        sizer.Add( text, 0, wx.LEFT | wx.EXPAND, 4 )
        
        # Set-up the layout:
        panel.SetSizerAndFit( sizer )
        label_lo.SetLabel( str(low)  )
        label_hi.SetLabel( str(high) )
        self.set_tooltip( slider )
        self.set_tooltip( label_lo )
        self.set_tooltip( label_hi )
        self.set_tooltip( text )

        # Hook up the traits to listen to the object.
        self.sync_value( factory.low_name,  'low',  'from' )
        self.sync_value( factory.high_name, 'high', 'from' )

        # Update the ranges and button just in case.
        self.update_range_ui()
       
    #---------------------------------------------------------------------------
    #  Handles the user changing the current slider value: 
    #---------------------------------------------------------------------------
    
    def update_object_on_scroll ( self, event ):
        """ Handles the user changing the current slider value.
        """
        low   = self.cur_low
        high  = self.cur_high
        value = low + ((float( event.GetPosition() ) / 10000.0) * 
                       (high - low))
        self.control.text.SetValue( self._format % value )
        event_type = event.GetEventType()
        try:
            self.ui_changing = True
            if ((event_type == wx.wxEVT_SCROLL_ENDSCROLL) or
                (self.factory.auto_set and 
                 (event_type == wx.wxEVT_SCROLL_THUMBTRACK))):
                if self.factory.is_float:
                    self.value = value
                else:
                    self.value = int( value )
        finally:
            self.ui_changing = False
        
    #---------------------------------------------------------------------------
    #  Handle the user pressing the 'Enter' key in the edit control:
    #---------------------------------------------------------------------------
    
    def update_object_on_enter ( self, event ):
        """ Handles the user pressing the Enter key in the text field.
        """
        low  = self.cur_low
        high = self.cur_high        
        try:
            self.value = value = eval( self.control.text.GetValue().strip() )
        except TraitError, excp:
            pass
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
    
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        value = self.value
        low   = self.low
        high  = self.high
        try:
            text = self._format % value
            1 / (low <= value <= high)
        except:
            value = low
        self.value = value
        if not self.ui_changing:
            self.init_range()
            self.update_range_ui()

    def update_range_ui ( self ):
        """ Updates the slider range controls.
        """
        low, high = self.cur_low, self.cur_high
        value = self.value
        self._set_format()
        self.control.label_lo.SetLabel( self._format % low )
        self.control.label_hi.SetLabel( self._format % high )
        ivalue = int( (float( value - low ) / (high - low)) * 10000.0 )
        self.control.slider.SetValue( ivalue )
        text = self._format % self.value
        self.control.text.SetValue( text )
        factory = self.factory
        f_low, f_high = self.low, self.high
        if low == f_low:
            self.control.button_lo.Disable()
        else:
            self.control.button_lo.Enable()
        if high == f_high:
            self.control.button_hi.Disable()
        else:
            self.control.button_hi.Enable()        

    def init_range ( self ):
        """ Initializes the slider range controls.
        """
        value     = self.value
        factory   = self.factory
        low, high = self.low, self.high
        if high is None and low is not None:
            high = -low
        mag       = abs( value )
        if mag <= 10.0:
            cur_low  = max( value - 10, low )
            cur_high = min( value + 10, high )
        else:
            d        = 0.5 * (10**int( log10( mag ) + 1 ))
            cur_low  = max( low,  value - d )
            cur_high = min( high, value + d )
                
        self.cur_low, self.cur_high = cur_low, cur_high

    def reduce_range ( self, event ):
        """ Reduces the extent of the displayed range.
        """
        factory   = self.factory
        low, high = self.low, self.high
        if abs( self.cur_low ) < 10:
            self.cur_low  = max( -10, low )
            self.cur_high = min( 10, high )
        elif self.cur_low > 0:
            self.cur_high = self.cur_low
            self.cur_low  = max( low, self.cur_low / 10 )
        else:
            self.cur_high = self.cur_low
            self.cur_low  = max( low, self.cur_low * 10 )
                
        self.ui_changing = True
        self.value       = min( max( self.value, self.cur_low ), self.cur_high )
        self.ui_changing = False
        self.update_range_ui()

    def increase_range ( self, event ):
        """ Increased the extent of the displayed range.
        """
        factory   = self.factory
        low, high = self.low, self.high
        if abs( self.cur_high ) < 10:
            self.cur_low  = max( -10, low )
            self.cur_high = min(  10, high )
        elif self.cur_high > 0:
            self.cur_low  = self.cur_high
            self.cur_high = min( high, self.cur_high * 10 )
        else:
            self.cur_low  = self.cur_high
            self.cur_high = min( high, self.cur_high / 10 )

        self.ui_changing = True
        self.value       = min( max( self.value, self.cur_low ), self.cur_high )
        self.ui_changing = False
        self.update_range_ui()

    def _set_format ( self ):
        self._format = '%d'
        factory      = self.factory
        low, high    = self.cur_low, self.cur_high
        diff         = high - low
        if factory.is_float:
            if diff > 99999:
                self._format = '%.2g'
            elif diff > 1:
                self._format = '%%.%df' % max( 0, 4 -
                                                  int( log10( high - low ) ) )
            else:
                self._format = '%.3f'

    #---------------------------------------------------------------------------
    #  Handles the 'low'/'high' traits being changed:  
    #---------------------------------------------------------------------------

    def _low_changed ( self, low ):
        if self.value < low:
            if self.factory.is_float:
                self.value = float( low )
            else:
                self.value = int( low )
                
        self.update_editor()
            
    def _high_changed ( self, high ):
        if self.value > high:
            if self.factory.is_float:
                self.value = float( high )
            else:
                self.value = int( high )

        self.update_editor()

#-------------------------------------------------------------------------------
#  'SimpleSpinEditor' class:
#-------------------------------------------------------------------------------

class SimpleSpinEditor ( Editor ):
    """ A simple style of range editor that displays a spin box control.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # Low value for the slider range
    low = Any
    
    # High value for the slider range
    high = Any

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        if not factory.low_name:
            self.low = factory.low
        if not factory.high_name:
            self.high = factory.high
        self.sync_value( factory.low_name,  'low',  'from' )
        self.sync_value( factory.high_name, 'high', 'from' )
        low  = self.low
        high = self.high
        self.control = wx.SpinCtrl( parent, -1, self.str_value,
                                    min     = low,
                                    max     = high,
                                    initial = self.value )
        wx.EVT_SPINCTRL( parent, self.control.GetId(), self.update_object )
        if sys.platform.startswith( 'win' ):
            wx.EVT_TEXT( parent, self.control.GetId(), self.update_object )

    #---------------------------------------------------------------------------
    #  Handle the user selecting a new value from the spin control:
    #---------------------------------------------------------------------------
  
    def update_object ( self, event ):
        """ Handles the user selecting a new value in the spin box.
        """
        self._locked = True
        try:
            self.value = self.control.GetValue()
        finally:
            self._locked = False

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        if not self._locked:
            try:
                self.control.SetValue( int( self.value ) )
            except:
                pass
                                      
    #---------------------------------------------------------------------------
    #  Handles the 'low'/'high' traits being changed:  
    #---------------------------------------------------------------------------

    def _low_changed ( self, low ):
        if self.value < low:
            if self.factory.is_float:
                self.value = float( low )
            else:
                self.value = int( low )

        if self.control:
            self.control.SetRange( self.low, self.high )
            self.control.SetValue( int( self.value ) )
            
    def _high_changed ( self, high ):
        if self.value > high:
            if self.factory.is_float:
                self.value = float( high )
            else:
                self.value = int( high )

        if self.control:
            self.control.SetRange( self.low, self.high )
            self.control.SetValue( int( self.value ) )

#-------------------------------------------------------------------------------
#  'RangeTextEditor' class:
#-------------------------------------------------------------------------------
                               
class RangeTextEditor ( TextEditor ):
    """ Editor for ranges that displays a text field. If the user enters a 
    value that is outside the allowed range, the background of the field
    changes color to indicate an error.
    """
    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------
  
    def update_object ( self, event ):
        """ Handles the user entering input data in the edit control.
        """
        try:
            self.value = eval( self.control.GetValue() )
            self.control.SetBackgroundColour( OKColor )
        except:
            self.control.SetBackgroundColour( ErrorColor )
        self.control.Refresh()
        
#-------------------------------------------------------------------------------
#  'SimpleEnumEditor' factory adaptor:  
#-------------------------------------------------------------------------------

def SimpleEnumEditor ( parent, factory, ui, object, name, description ):
    return CustomEnumEditor( parent, factory, ui, object, name, description,
                             'simple' )
        
#-------------------------------------------------------------------------------
#  'CustomEnumEditor' factory adaptor:  
#-------------------------------------------------------------------------------

def CustomEnumEditor ( parent, factory, ui, object, name, description, 
                       style = 'custom' ):
    """ Factory adapter that returns a enumeration editor of the specified 
    style.
    """
    if factory._enum is None:
        import enum_editor
        factory._enum = enum_editor.ToolkitEditorFactory( 
                            values = range( factory.low, factory.high + 1 ), 
                            cols   = factory.cols )
                            
    if style == 'simple':
        return factory._enum.simple_editor( ui, object, name, description, 
                                            parent )
    
    return factory._enum.custom_editor( ui, object, name, description, parent )
       
#-------------------------------------------------------------------------------
#  Defines the mapping between editor factory 'mode's and Editor classes:  
#-------------------------------------------------------------------------------

# Mapping between editor factory modes and simple editor classes
SimpleEditorMap = {
    'slider':  SimpleSliderEditor, 
    'xslider': LargeRangeSliderEditor,
    'spinner': SimpleSpinEditor,
    'enum':    SimpleEnumEditor,
    'text':    RangeTextEditor
}
# Mapping between editor factory modes and custom editor classes
CustomEditorMap = {
    'slider':  SimpleSliderEditor, 
    'xslider': LargeRangeSliderEditor,
    'spinner': SimpleSpinEditor,
    'enum':    CustomEnumEditor,
    'text':    RangeTextEditor
}

