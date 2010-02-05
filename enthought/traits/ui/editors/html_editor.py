#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
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

""" Defines the HTML editor factory. HTML editors interpret and display 
    HTML-formatted text, but do not modify it.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ...api import Str, false
    
from ..basic_editor_factory import BasicEditorFactory
    
from ..toolkit import toolkit_object
                    
# Callable that returns the editor to use in the UI.
def html_editor(*args, **traits):
    return toolkit_object('html_editor:SimpleEditor')(*args, **traits)

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Template used to create code blocks embedded in the module comment
block_template = """<center><table width="95%%"><tr><td bgcolor="#ECECEC"><tt>
%s</tt></td></tr></table></center>"""

# Template used to create lists embedded in the module comment
list_template = """<%s>
%s
</%s>"""

#------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#------------------------------------------------------------------------------

class ToolkitEditorFactory ( BasicEditorFactory ):
    """ Editor factory for HTML editors.
    """
    #--------------------------------------------------------------------------
    #  Trait definitions:  
    #--------------------------------------------------------------------------
    
    # Should implicit text formatting be converted to HTML?
    format_text = false

    # External objects referenced in the HTML are relative to this url
    base_url = Str

    # The object trait containing the base URL
    base_url_name = Str

    # Should links be opened in an external browser?
    open_externally = false

    #---------------------------------------------------------------------------
    #  Parses the contents of a formatted text string into the corresponding 
    #  HTML:
    #---------------------------------------------------------------------------
    
    def parse_text ( self, text ):
        """ Parses the contents of a formatted text string into the 
            corresponding HTML.
        """
        text  = text.replace( '\r\n', '\n' )
        lines = [ ('.' + line).strip()[1:] for line in text.split( '\n' ) ]
        ind   = min( *([ self.indent( line ) for line in lines
                         if line != '' ] + [ 1000, 1000 ]) )
        if ind >= 1000:
            ind = 0
        lines     = [ line[ ind: ] for line in lines ]
        new_lines = []
        i = 0
        n = len( lines )
        while i < n:
            line = lines[i]
            m    = self.indent( line )
            if m > 0:
                if line[m] in '-*':
                    i, line = self.parse_list( lines, i )
                else:
                    i, line = self.parse_block( lines, i )
                new_lines.append( line ) 
            else:
                new_lines.append( line )
                i += 1
        text       = '\n'.join( new_lines )
        paragraphs = [ p.strip() for p in text.split( '\n\n' ) ]
        for i, paragraph in enumerate( paragraphs ):
            if paragraph[:3].lower() != '<p>':
                paragraphs[i] = '<p>%s</p>' % paragraph
        return '\n'.join( paragraphs )
      
    #---------------------------------------------------------------------------
    #  Parses a code block:  
    #---------------------------------------------------------------------------
                    
    def parse_block ( self, lines, i ):
        """ Parses a code block.
        """
        m = 1000
        n = len( lines )
        j = i
        while j < n:
            line = lines[j]
            if line != '':
                k = self.indent( line )
                if k == 0:
                    break
                m = min( m, k )
            j += 1
        j -= 1
        while (j > i) and (lines[j] == ''):
            j -= 1
        j += 1
        temp = [ (('&nbsp;' * (self.indent( line ) - m)) + 
                  line.strip()) for line in lines[ i: j ] ]
        return ( j, block_template % '\n<br>'.join( temp ) )
        
    #---------------------------------------------------------------------------
    #  Parses a list:  
    #---------------------------------------------------------------------------
            
    def parse_list ( self, lines, i ):
        """ Parses a list.
        """
        line   = lines[i]
        m      = self.indent( line )
        kind   = line[m]
        result = [ '<li>' + line[ m + 1: ].strip() ]
        n      = len( lines )
        j      = i + 1
        while j < n:
            line = lines[j]
            k    = self.indent( line )
            if k < m:
                break
            if k == m:
                if line[k] != kind:
                    break
                result.append( '<li>' + line[ k + 1: ].strip() )
                j += 1
            elif line[k] in '-*':
                j, line = self.parse_list( lines, j )
                result.append( line )
            else:
                result.append( line.strip() )
                j += 1
        style = [ 'ul', 'ol' ][ kind == '*' ]
        return ( j, list_template % ( style, '\n'.join( result ), style ) )
        
    #---------------------------------------------------------------------------
    #  Calculates the amount of white space at the beginning of a line:  
    #---------------------------------------------------------------------------
                    
    def indent ( self, line ):
        """ Calculates the amount of white space at the beginning of a line.
        """
        return len( line ) - len( (line + '.').strip() ) + 1
    
HTMLEditor = ToolkitEditorFactory(klass = html_editor)

#-EOF--------------------------------------------------------------------------
