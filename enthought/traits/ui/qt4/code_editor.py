#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines a source code editor and code editor factory, for the PyQt user
    interface toolkit, useful for tools such as debuggers.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui, Qsci

from enthought.traits.api \
    import Instance, Str, List, Int, Color, Enum, Event, Bool, TraitError
    
from enthought.traits.ui.key_bindings \
    import KeyBindings
    
from enthought.pyface.api \
    import PythonEditor
    
from editor \
    import Editor
    
from editor_factory \
    import EditorFactory
    
from constants \
    import OKColor, ErrorColor

#-------------------------------------------------------------------------------
#  Constants:  
#-------------------------------------------------------------------------------
        
# Marker line constants:

# Marks a marked line
MARK_MARKER = 0 

# Marks a line matching the current search
SEARCH_MARKER = 1  

# Marks the currently selected line
SELECTED_MARKER = 2    

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ PyQt editor factory for code editors.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Object trait containing list of line numbers to mark (optional)
    mark_lines = Str
    
    # Background color for marking lines
    mark_color = Color( 0xECE9D8 )
    
    # Object trait containing the currently selected line (optional)
    selected_line = Str
    
    # Object trait containing the currently selected text (optional)
    selected_text = Str
    
    # Background color for selected lines
    selected_color = Color( 0xA4FFFF )
    
    # Where should the search toolbar be placed?
    search = Enum( 'top', 'bottom', 'none' )
    
    # Background color for lines that match the current search
    search_color = Color( 0xFFFF94 )
    
    # Current line
    line = Str
    
    # Current column
    column = Str
    
    # Should code folding be enabled?
    foldable = Bool( True )
    
    # Should line numbers be displayed in the margin?
    show_line_numbers = Bool( True )
    
    # Is user input set on every change?
    auto_set = Bool( True )
    
    # Should the editor auto-scroll when a new **selected_line** value is set?
    auto_scroll = Bool( True )

    # Optional key bindings associated with the editor    
    key_bindings = Instance( KeyBindings )
    
    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------
    
    def simple_editor ( self, ui, object, name, description, parent ):
        return SourceEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description,
                             readonly    = False )
    
    def readonly_editor ( self, ui, object, name, description, parent ):
        return SourceEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description,
                             readonly    = True )
                                      
#-------------------------------------------------------------------------------
#  'SourceEditor' class:
#-------------------------------------------------------------------------------
                               
class SourceEditor ( Editor ):
    """ Editor for source code, which displays a PyFace PythonEditor.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # The code editor is scrollable. This value overrides the default.
    scrollable = True
    
    # Is the editor read only?
    readonly = Bool( False )
    
    # The currently selected line
    selected_line = Int
    
    # The currently selected text
    selected_text = Str
    
    # The list of line numbers to mark
    mark_lines = List( Int )
    
    # The current line number
    line = Event
    
    # The current column
    column = Event
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        self._editor = editor = PythonEditor(parent,
                show_line_numbers = factory.show_line_numbers)
        self.control = control = editor.control

        control.connect(control, QtCore.SIGNAL('lostFocus'), self.update_object)

        if factory.auto_set:
            editor.on_trait_change( self.update_object, 'changed', 
                                    dispatch = 'ui' )
        if factory.key_bindings is not None:
            editor.on_trait_change( self.key_pressed, 'key_pressed', 
                                    dispatch = 'ui' )
        if self.readonly:
            control.setReadOnly(True)
            
        # Define the markers we use:
        control.markerDefine(Qsci.QsciScintilla.Background, MARK_MARKER)
        control.setMarkerBackgroundColor(factory.mark_color_, MARK_MARKER)

        control.markerDefine(Qsci.QsciScintilla.Background, SEARCH_MARKER)
        control.setMarkerBackgroundColor(factory.search_color_, SEARCH_MARKER)

        control.markerDefine(Qsci.QsciScintilla.Background, SELECTED_MARKER)
        control.setMarkerBackgroundColor(factory.selected_color_, SELECTED_MARKER)

        # Make sure the editor has been initialized:
        self.update_editor()
        
        # Set up any event listeners:
        self.sync_value( factory.mark_lines, 'mark_lines', 'from',
                         is_list = True )
        self.sync_value( factory.selected_line, 'selected_line', 'from' )
        self.sync_value( factory.selected_text, 'selected_text', 'to' )
        self.sync_value( factory.line, 'line' )
        self.sync_value( factory.column, 'column' )

        # Check if we need to monitor the line or column position being changed:
        if (factory.line != '') or (factory.column != ''):
            control.connect(control,
                    QtCore.SIGNAL('cursorPositionChanged(int, int)'),
                    self._position_changed)
            
    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------

    def update_object ( self ):
        """ Handles the user entering input data in the edit control.
        """
        if not self._locked:
            try:
                self.value = unicode(self.control.text())
                self.control.lexer().setPaper(OKColor)
            except TraitError, excp:
                pass
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        self._locked = True
        new_value = self.str_value
        control = self.control
        if control.text() != new_value:
            readonly = control.isReadOnly()
            control.setReadOnly(False)
            vsb = control.verticalScrollBar()
            l1 = vsb.value()
            line, column = control.getCursorPosition()
            control.setText(new_value)
            control.setCursorPosition(line, column)
            vsb.setValue(l1)
            control.setReadOnly(readonly)
            self._mark_lines_changed()
            self._selected_line_changed()
        self._locked = False
        
    #---------------------------------------------------------------------------
    #  Handles the set of 'marked lines' being changed:  
    #---------------------------------------------------------------------------
                
    def _mark_lines_changed ( self ):
        """ Handles the set of marked lines being changed.
        """
        lines   = self.mark_lines
        control = self.control
        lc      = control.lines()
        control.markerDeleteAll(MARK_MARKER)
        for line in lines:
            if 0 < line <= lc:
                control.markerAdd(line - 1, MARK_MARKER)

    def _mark_lines_items_changed ( self ):
        self._mark_lines_changed()
        
    #---------------------------------------------------------------------------
    #  Handles the currently 'selected line' being changed:  
    #---------------------------------------------------------------------------
                
    def _selected_line_changed ( self ):
        """ Handles a change in which line is currently selected.
        """
        line    = self.selected_line
        control = self.control
        line    = max(1, min(control.lines(), line)) - 1
        control.markerDeleteAll(SELECTED_MARKER)
        control.markerAdd(line, SELECTED_MARKER)
        _, column = control.getCursorPosition()
        control.setCursorPosition(line, column)
        if self.factory.auto_scroll:
            control.ensureLineVisible(line)

    #---------------------------------------------------------------------------
    #  Handles the 'line' trait being changed:  
    #---------------------------------------------------------------------------
                                              
    def _line_changed ( self, line ):
        if not self._locked:
            _, column = control.getCursorPosition()
            self.control.setCursorPosition(line - 1, column)
                                  
    #---------------------------------------------------------------------------
    #  Handles the 'column' trait being changed:  
    #---------------------------------------------------------------------------
                                              
    def _column_changed ( self, column ):
        if not self._locked:
            line, _ = control.getCursorPosition()
            self.control.setCursorPosition(line, column - 1)

    #---------------------------------------------------------------------------
    #  Handles the cursor position being changed:  
    #---------------------------------------------------------------------------
                        
    def _position_changed(self, line, column):
        """ Handles the cursor position being changed.
        """
        self._locked = True
        self.line = line
        self.column = column
        self._locked = False
        self.selected_text = unicode(control.selectedText())
        
    #---------------------------------------------------------------------------
    #  Handles a key being pressed within the editor:    
    #---------------------------------------------------------------------------
                
    def key_pressed ( self, event ):
        """ Handles a key being pressed within the editor.
        """
        self.factory.key_bindings.do( event.event, self.ui.handler, 
                                      self.ui.info )
        
    #---------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #---------------------------------------------------------------------------
        
    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's trait value.
        """
        self.control.lexer().setPaper(ErrorColor)

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:    
    #---------------------------------------------------------------------------
                
    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        super( SourceEditor, self ).dispose()
        if self.factory.auto_set:
            self._editor.on_trait_change( self.update_object, 'changed',
                                          remove = True )
        if self.factory.key_bindings is not None:
            self._editor.on_trait_change( self.key_pressed, 'key_pressed',
                                          remove = True )
                                          
    #-- UI preference save/restore interface -----------------------------------

    #---------------------------------------------------------------------------
    #  Restores any saved user preference information associated with the 
    #  editor:
    #---------------------------------------------------------------------------
            
    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the 
            editor.
        """
        if self.factory.key_bindings is not None:
            key_bindings = prefs.get( 'key_bindings' )
            if key_bindings is not None:
                self.factory.key_bindings.merge( key_bindings )
            
    #---------------------------------------------------------------------------
    #  Returns any user preference information associated with the editor:
    #---------------------------------------------------------------------------
            
    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        return { 'key_bindings': self.factory.key_bindings }
