#------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   10/21/2004
#
#------------------------------------------------------------------------------
""" Defines the range editor factory for all traits user interface toolkits.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ...api import (CTrait, Property, Range, Enum, Str, Int, Any, Unicode,
        Bool, Undefined)

# CIRCULAR IMPORT FIXME: Importing from the source rather than traits.ui.api
# to avoid circular imports, as this EditorFactory will be part of
# traits.ui.api as well.
from ..view import View

from ..editor_factory import EditorFactory

from ..toolkit import toolkit_object

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ Editor factory for range editors.
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

    # FIXME: This is supported only in the wx backend so far.
    # The width of the low and high labels
    label_width = Int

    # The name of an [object.]trait that defines the low value for the range
    low_name = Str

    # The name of an [object.]trait that defines the high value for the range
    high_name = Str

    # Formatting string used to format value and labels
    format = Unicode( '%s' )

    # Is the range for floating pointer numbers (vs. integers)?
    is_float = Bool( Undefined )

    # Function to evaluate floats/ints when they are assigned to an object trait
    evaluate = Any

    # The object trait containing the function used to evaluate floats/ints
    evaluate_name = Str

    # Low end of range
    low = Property

    # High end of range
    high = Property

    # Display mode to use
    mode = Enum( 'auto', 'slider', 'xslider', 'spinner', 'enum', 'text', 'logslider' )

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
        if self.is_float is Undefined:
            self.is_float = isinstance( low, float )

        if (self.low_label == '') or (self.low_label == unicode(old_low)):
            self.low_label = unicode(low)

    def _get_high ( self ):
        return self._high

    def _set_high ( self, high ):
        old_high          = self._high
        self._high = high = self._cast( high )
        if self.is_float is Undefined:
            self.is_float = isinstance( high, float )

        if (self.high_label == '') or (self.high_label == unicode(old_high)):
            self.high_label = unicode(high)

    def _cast ( self, value ):
        if not isinstance( value, basestring ):
            return value

        try:
            return int( value )
        except ValueError:
            return float( value )

    #-- Private Methods --------------------------------------------------------

    def _get_low_high ( self, ui ):
        """ Returns the low and high values used to determine the initial range.
        """
        low, high = self.low, self.high

        if (low is None) and (self.low_name != ''):
            low = self.named_value( self.low_name, ui )
            if self.is_float is Undefined:
                self.is_float = isinstance( low, float )

        if (high is None) and (self.high_name != ''):
            high = self.named_value( self.high_name, ui )
            if self.is_float is Undefined:
                self.is_float = isinstance( high, float )

        if self.is_float is Undefined:
            self.is_float = True

        return ( low, high, self.is_float )

    #---------------------------------------------------------------------------
    #  Property getters.
    #---------------------------------------------------------------------------
    def _get_simple_editor_class( self ):
        """ Returns the editor class to use for a simple style.

        The type of editor depends on the type and extent of the range being
        edited:

        * One end of range is unspecified: RangeTextEditor
        * **mode** is specified and not 'auto': editor corresponding to **mode**
        * Floating point range with extent > 100: LargeRangeSliderEditor
        * Integer range or floating point range with extent <= 100:
          SimpleSliderEditor
        * All other cases: SimpleSpinEditor
        """
        low, high, is_float = self._low_value, self._high_value, self.is_float

        if (low is None) or (high is None):
            return toolkit_object('range_editor:RangeTextEditor')

        if (not is_float) and (abs(high - low) > 1000000000L):
            return toolkit_object('range_editor:RangeTextEditor')

        if self.mode != 'auto':
            return toolkit_object('range_editor:SimpleEditorMap')[ self.mode ]

        if is_float and (abs(high - low) > 100):
            return toolkit_object('range_editor:LargeRangeSliderEditor')

        if is_float or (abs(high - low) <= 100):
            return toolkit_object('range_editor:SimpleSliderEditor')

        return toolkit_object('range_editor:SimpleSpinEditor')

    def _get_custom_editor_class ( self ):
        """ Creates a custom style of range editor

        The type of editor depends on the type and extent of the range being
        edited:

        * One end of range is unspecified: RangeTextEditor
        * **mode** is specified and not 'auto': editor corresponding to **mode**
        * Floating point range: Same as "simple" style
        * Integer range with extent > 15: Same as "simple" style
        * Integer range with extent <= 15: CustomEnumEditor

        """
        low, high, is_float = self._low_value, self._high_value, self.is_float
        if (low is None) or (high is None):
            return toolkit_object('range_editor:RangeTextEditor')

        if self.mode != 'auto':
            return toolkit_object('range_editor:CustomEditorMap')[ self.mode ]

        if is_float or (abs(high - low) > 15):
           return self.simple_editor_class

        return toolkit_object('range_editor:CustomEnumEditor')

    def _get_text_editor_class( self ):
        """Returns the editor class to use for a text style.
        """
        return toolkit_object('range_editor:RangeTextEditor')

    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------

    def simple_editor ( self, ui, object, name, description, parent ):
        """ Generates an editor using the "simple" style.
        Overridden to set the values of the _low_value, _high_value and
        is_float traits.

        """
        self._low_value, self._high_value, self.is_float = self._get_low_high(ui)
        return super(RangeEditor, self).simple_editor(ui, object, name, description, parent)

    def custom_editor ( self, ui, object, name, description, parent ):
        """ Generates an editor using the "custom" style.
        Overridden to set the values of the _low_value, _high_value and
        is_float traits.

        """
        self._low_value, self._high_value, self.is_float = self._get_low_high(ui)
        return super(RangeEditor, self).custom_editor(ui, object, name, description, parent)


# Define the RangeEditor class
RangeEditor = ToolkitEditorFactory

### EOF ---------------------------------------------------------------------
