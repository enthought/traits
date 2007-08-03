#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
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

from enthought.traits.api \
    import CTrait, Enum, false, Int, Property, Range, Str, true, Unicode

from editor_factory \
    import EditorFactory

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ PyQt editor factory for text editors.
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
    low_label = Unicode

    # Label for the high end of the range
    high_label = Unicode

    # The width of the low and high labels
    label_width = Int

    # The name of an [object.]trait that defines the low value for the range
    low_name = Str

    # The name of an [object.]trait that defines the high value for the range
    high_name = Str

    # Formatting string used to format value and labels
    format = Unicode( '%s' )

    # Is the range for floating pointer numbers (vs. integers)?
    is_float = true

    # Low end of range
    low = Property

    # High end of range
    high = Property

    # Display mode to use
    mode = Enum( 'auto', 'slider', 'xslider', 'spinner', 'enum', 'text' )

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
