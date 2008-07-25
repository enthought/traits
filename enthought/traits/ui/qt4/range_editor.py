#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the various range editors and the range editor factory, for the
PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import log10

from PyQt4 import QtCore, QtGui

from enthought.traits.api \
     import CTrait, TraitError, Property, Range, Enum, Str, Int, Float, Any, \
            Unicode, Bool

from enthought.traits.ui.api \
    import View

from editor_factory \
    import EditorFactory, TextEditor

from editor \
    import Editor

from constants \
    import OKColor, ErrorColor

from helper \
    import IconButton

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ PyQt editor factory for range editors.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Number of columns when displayed as an enumeration
    cols = Range( 1, 20 )

    # Is user input set on every keystroke?
    auto_set = Bool(True)

    # Is user input set when the Enter key is pressed?
    enter_set = Bool(False)

    # Label for the low end of the range
    low_label = Unicode

    # Label for the high end of the range
    high_label = Unicode

    # FIXME: This is not yet supported.
    # The width of the low and high labels
    label_width = Int

    # The name of an [object.]trait that defines the low value for the range
    low_name = Str

    # The name of an [object.]trait that defines the high value for the range
    high_name = Str

    # Formatting string used to format value and labels
    format = Unicode( '%s' )

    # Is the range for floating pointer numbers (vs. integers)?
    is_float = Bool(True)

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

            if self.low_name == '':
                self.low  = handler._low

            if self.high_name == '':
                self.high = handler._high
        else:
            if (self.low is None) and (self.low_name == ''):
                self.low  = 0.0

            if (self.high is None) and (self.high_name == ''):
                self.high = 1.0

    #---------------------------------------------------------------------------
    #  Define the 'low' and 'high' traits:
    #---------------------------------------------------------------------------

    def _get_low ( self ):
        return self._low

    def _set_low ( self, low ):
        old_low         = self._low
        self._low = low = self._cast( low )
        self.is_float   = isinstance(low, float)

        if (self.low_label == '') or (self.low_label == unicode(old_low)):
            self.low_label = unicode(low)

    def _get_high ( self ):
        return self._high

    def _set_high ( self, high ):
        old_high          = self._high
        self._high = high = self._cast( high )
        self.is_float     = isinstance(high, float)

        if (self.high_label == '') or (self.high_label == unicode(old_high)):
            self.high_label = unicode(high)

    def _cast ( self, value ):
        if type( value ) is not str:
            return value

        try:
            return int( value )
        except:
            return float( value )

    #-- Private Methods --------------------------------------------------------

    def _get_low_high ( self, ui ):
        """ Returns the low and high values used to determine the initial range.
        """
        low, high = self.low, self.high

        if (low is None) and (self.low_name != ''):
            low           = self.named_value( self.low_name, ui )
            self.is_float = isinstance( low, float )

        if (high is None) and (self.high_name != ''):
            high          = self.named_value( self.high_name, ui )
            self.is_float = isinstance( low, float )

        return ( low, high, self.is_float )

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
        low, high, is_float = self._get_low_high(ui)

        if (low is None) or (high is None):
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

        if is_float and (abs(high - low) > 100):
            return LargeRangeSliderEditor( parent,
                                       factory     = self,
                                       ui          = ui,
                                       object      = object,
                                       name        = name,
                                       description = description )

        if is_float or (abs(high - low) <= 100):
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
        low, high, is_float = self._get_low_high(ui)

        if (low is None) or (high is None):
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

        if is_float or (abs(high - low) > 15):
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
    format = Unicode

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

        if factory.label_width > 0:
            size = wx.Size( factory.label_width, 20 )

        self.sync_value( factory.low_name,  'low',  'from' )
        self.sync_value( factory.high_name, 'high', 'from' )
        low  = self.low
        high = self.high

        # The control is a horizontal layout.
        self.control = panel = QtGui.QHBoxLayout()

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

            if ivalue is None:
                ivalue = 0

        self._label_lo = QtGui.QLabel()
        self._label_lo.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        panel.addWidget(self._label_lo)

        panel.slider = slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        slider.setTracking(factory.auto_set)
        slider.setMinimum(0)
        slider.setMaximum(10000)
        slider.setPageStep(1000)
        slider.setSingleStep(100)
        slider.setValue(ivalue)
        QtCore.QObject.connect(slider, QtCore.SIGNAL('valueChanged(int)'),
                self.update_object_on_scroll)
        panel.addWidget(slider)

        self._label_hi = QtGui.QLabel()
        panel.addWidget(self._label_hi)

        panel.text = text = QtGui.QLineEdit(fvalue_text)
        QtCore.QObject.connect(text, QtCore.SIGNAL('editingFinished()'),
                self.update_object_on_enter)

        # The default size is a bit too big and probably doesn't need to grow.
        sh = text.sizeHint()
        sh.setWidth(sh.width() / 2)
        text.setMaximumSize(sh)

        panel.addWidget(text)

        low_label = factory.low_label
        if factory.low_name != '':
            low_label = self.format % self.low

        high_label = factory.high_label
        if factory.high_name != '':
            high_label = self.format % self.high

        self._label_lo.setText(low_label)
        self._label_hi.setText(high_label)

        self.set_tooltip(slider)
        self.set_tooltip(self._label_lo)
        self.set_tooltip(self._label_hi)
        self.set_tooltip(text)

    #---------------------------------------------------------------------------
    #  Handles the user changing the current slider value:
    #---------------------------------------------------------------------------

    def update_object_on_scroll(self, pos):
        """ Handles the user changing the current slider value.
        """
        value = self.low + ((float(pos) / 10000.0) * (self.high - self.low))

        if not self.factory.is_float:
            value = int(value)

        self.control.text.setText(self.format % value)
        self.value = value

    #---------------------------------------------------------------------------
    #  Handle the user pressing the 'Enter' key in the edit control:
    #---------------------------------------------------------------------------

    def update_object_on_enter (self):
        """ Handles the user pressing the Enter key in the text field.
        """
        try:
            try:
                value = eval(unicode(self.control.text.text()).strip())
            except Exception, ex:
                # The entered something that didn't eval as a number, (e.g.,
                # 'foo') pretend it didn't happen
                value = self.value
                self.control.text.setText(unicode(value))

            if not self.factory.is_float:
                value = int(value)

            self.value = value
            self.control.slider.setValue(
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

            if ivalue is None:
                ivalue = 0

        self.control.text.setText(text)

        blocked = self.control.slider.blockSignals(True)
        self.control.slider.setValue(ivalue)
        self.control.slider.blockSignals(blocked)

    #---------------------------------------------------------------------------
    #  Returns the editor's control for indicating error status:
    #---------------------------------------------------------------------------

    def get_error_control ( self ):
        """ Returns the editor's control for indicating error status.
        """
        return self.control.text

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
            self._label_lo.setText(self.format % low)
            self.update_editor()

    def _high_changed ( self, high ):
        if self.value > high:
            if self.factory.is_float:
                self.value = float( high )
            else:
                self.value = int( high )

        if self._label_hi is not None:
            self._label_hi.setText(self.format % high)
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
    ui_changing = Bool(False)

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory

        # Initialize using the factory range defaults:
        self.low = factory.low
        self.high = factory.high

        # Hook up the traits to listen to the object.
        self.sync_value( factory.low_name,  'low',  'from' )
        self.sync_value( factory.high_name, 'high', 'from' )

        self.init_range()
        low  = self.cur_low
        high = self.cur_high

        self._set_format()

        # The control is a horizontal layout.
        self.control = panel = QtGui.QHBoxLayout()

        fvalue = self.value

        try:
            fvalue_text = self._format % fvalue
            1 / (low <= fvalue <= high)
        except:
            fvalue_text = ''
            fvalue      = low

        if high > low:
            ivalue = int( (float( fvalue - low ) / (high - low)) * 10000 )
        else:
            ivalue = low

        # Lower limit label:
        panel.label_lo = label_lo = QtGui.QLabel()
        label_lo.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        panel.addWidget(label_lo)

        # Lower limit button:
        panel.button_lo = IconButton(QtGui.QStyle.SP_ArrowLeft,
                self.reduce_range)
        panel.addWidget(panel.button_lo)

        # Slider:
        panel.slider = slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        slider.setTracking(factory.auto_set)
        slider.setMinimum(0)
        slider.setMaximum(10000)
        slider.setPageStep(1000)
        slider.setSingleStep(100)
        slider.setValue(ivalue)
        QtCore.QObject.connect(slider, QtCore.SIGNAL('valueChanged(int)'),
                self.update_object_on_scroll)
        panel.addWidget(slider)

        # Upper limit button:
        panel.button_hi = IconButton(QtGui.QStyle.SP_ArrowRight,
                self.increase_range)
        panel.addWidget(panel.button_hi)

        # Upper limit label:
        panel.label_hi = label_hi = QtGui.QLabel()
        panel.addWidget(label_hi)

        # Text entry:
        panel.text = text = QtGui.QLineEdit(fvalue_text)
        QtCore.QObject.connect(text, QtCore.SIGNAL('editingFinished()'),
                self.update_object_on_enter)

        # The default size is a bit too big and probably doesn't need to grow.
        sh = text.sizeHint()
        sh.setWidth(sh.width() / 2)
        text.setMaximumSize(sh)

        panel.addWidget(text)

        label_lo.setText(str(low))
        label_hi.setText(str(high))
        self.set_tooltip(slider)
        self.set_tooltip(label_lo)
        self.set_tooltip(label_hi)
        self.set_tooltip(text)

        # Update the ranges and button just in case.
        self.update_range_ui()

    #---------------------------------------------------------------------------
    #  Handles the user changing the current slider value:
    #---------------------------------------------------------------------------

    def update_object_on_scroll(self, pos):
        """ Handles the user changing the current slider value.
        """
        value = self.cur_low + ((float(pos) / 10000.0) * (self.cur_high - self.cur_low))

        self.control.text.setText(self._format % value)

        if self.factory.is_float:
            self.value = value
        else:
            self.value = int(value)

    #---------------------------------------------------------------------------
    #  Handle the user pressing the 'Enter' key in the edit control:
    #---------------------------------------------------------------------------

    def update_object_on_enter(self):
        """ Handles the user pressing the Enter key in the text field.
        """
        try:
            self.value = eval(unicode(self.control.text.text()).strip())
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
        self.control.label_lo.setText( self._format % low )
        self.control.label_hi.setText( self._format % high )

        if high > low:
            ivalue = int( (float( value - low ) / (high - low)) * 10000.0 )
        else:
            ivalue = low

        blocked = self.control.slider.blockSignals(True)
        self.control.slider.setValue( ivalue )
        self.control.slider.blockSignals(blocked)

        text = self._format % self.value
        self.control.text.setText( text )
        self.control.button_lo.setEnabled(low != self.low)
        self.control.button_hi.setEnabled(high != self.high)

    def init_range ( self ):
        """ Initializes the slider range controls.
        """
        value     = self.value
        low, high = self.low, self.high
        if (high is None) and (low is not None):
            high = -low

        mag = abs( value )
        if mag <= 10.0:
            cur_low  = max( value - 10, low )
            cur_high = min( value + 10, high )
        else:
            d        = 0.5 * (10**int( log10( mag ) + 1 ))
            cur_low  = max( low,  value - d )
            cur_high = min( high, value + d )

        self.cur_low, self.cur_high = cur_low, cur_high

    def reduce_range(self):
        """ Reduces the extent of the displayed range.
        """
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

    def increase_range(self):
        """ Increased the extent of the displayed range.
        """
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
    #  Returns the editor's control for indicating error status:
    #---------------------------------------------------------------------------

    def get_error_control ( self ):
        """ Returns the editor's control for indicating error status.
        """
        return self.control.text

    #---------------------------------------------------------------------------
    #  Handles the 'low'/'high' traits being changed:
    #---------------------------------------------------------------------------

    def _low_changed ( self, low ):
        if self.control is not None:
            if self.value < low:
                if self.factory.is_float:
                    self.value = float( low )
                else:
                    self.value = int( low )

            self.update_editor()

    def _high_changed ( self, high ):
        if self.control is not None:
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

        self.control = QtGui.QSpinBox()
        self.control.setMinimum(low)
        self.control.setMaximum(high)
        self.control.setValue(self.value)
        QtCore.QObject.connect(self.control,
                QtCore.SIGNAL('valueChanged(int)'), self.update_object)
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handle the user selecting a new value from the spin control:
    #---------------------------------------------------------------------------

    def update_object(self, value):
        """ Handles the user selecting a new value in the spin box.
        """
        self._locked = True
        try:
            self.value = value
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
                self.control.setValue(int(self.value))
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
            self.control.setMinimum(low)
            self.control.setValue(int(self.value))

    def _high_changed ( self, high ):
        if self.value > high:
            if self.factory.is_float:
                self.value = float( high )
            else:
                self.value = int( high )

        if self.control:
            self.control.setMaximum(high)
            self.control.setValue(int(self.value))

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

    def update_object (self):
        """ Handles the user entering input data in the edit control.
        """
        try:
            self.value = eval(unicode(self.control.text()))
            col = OKColor
        except:
            col = ErrorColor

        pal = QtGui.QPalette(self.control.palette())
        pal.setColor(QtGui.QPalette.Base, col)
        self.control.setPalette(pal)

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
