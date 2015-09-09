#-------------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
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
#  Date:   03/30/2007
#
#  fixme:
#  - Get custom tree view images.
#  - Write a program to create a directory structure from a lesson plan file.
#
#-------------------------------------------------------------------------------

""" A framework for creating interactive Python tutorials.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys
import os
import re

from string \
    import capwords

from traits.api \
    import HasPrivateTraits, HasTraits, File, Directory, Instance, Int, Str, \
           List, Bool, Dict, Any, Property, Delegate, Button, cached_property

from traitsui.api \
    import View, VGroup, HGroup, VSplit, HSplit, Tabbed, Item, Heading, \
           Handler, ListEditor, CodeEditor, EnumEditor, HTMLEditor, \
           TreeEditor, TitleEditor, ValueEditor, ShellEditor

from traitsui.menu \
    import NoButtons

from traitsui.tree_node \
    import TreeNode

from pyface.image_resource \
    import ImageResource

try:
    from traitsui.wx.extra.windows.ie_html_editor \
        import IEHTMLEditor

    from traitsui.wx.extra.windows.flash_editor \
        import FlashEditor
except:
    IEHTMLEditor = FlashEditor = None

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Correct program usage information:
Usage = """
Correct usage is: tutor.py [root_dir]
where:
    root_dir = Path to root of the tutorial tree

If omitted, 'root_dir' defaults to the current directory."""

# The standard list editor used:
list_editor = ListEditor(
    use_notebook = True,
    deletable    = False,
    page_name    = '.title',
    export       = 'DockWindowShell',
    dock_style   = 'fixed'
)

# The standard code snippet editor used:
snippet_editor = ListEditor(
    use_notebook = True,
    deletable    = False,
    page_name    = '.title',
    export       = 'DockWindowShell',
    dock_style   = 'tab',
    selected     = 'snippet'
)

# Regular expressions used to match section directories:
dir_pat1 = re.compile( r'^(\d\d\d\d)_(.*)$' )
dir_pat2 = re.compile( r'^(.*)_(\d+\.\d+)$' )

# Regular expression used to match section header in a Python source file:
section_pat1 = re.compile( r'^#-*\[(.*)\]' )  # Normal
section_pat2 = re.compile( r'^#-*<(.*)>' )    # Hidden
section_pat3 = re.compile( r'^#-*\((.*)\)' )  # Description

# Regular expression used to extract item titles from URLs:
url_pat1 = re.compile( r'^(.*)\[(.*)\](.*)$' )  # Normal

# Is this running on the Windows platform?
is_windows = (sys.platform in ( 'win32', 'win64' ))

# Python file section types:
IsCode        = 0
IsHiddenCode  = 1
IsDescription = 2

# HTML template for a default lecture:
DefaultLecture = """<html>
  <head>
  </head>
  <body>
    <p>This section contains the following topics:</p>
    <ul>
    %s
    </ul>
  </body>
</html>
"""

# HTML template for displaying a .wmv/.avi movie file:
WMVMovieTemplate = """<html>
<head>
</head>
<body>
<p><object classid="clsid:22D6F312-B0F6-11D0-94AB-0080C74C7E95" codebase="http://activex.microsoft.com/activex/controls/mplayer/en/nsmp2inf.cab#Version=6,4,5,715">
<param name="FileName" value="%s">
<param name="AutoStart" value="true">
<param name="ShowTracker" value="true">
<param name="ShowControls" value="true">
<param name="ShowGotoBar" value="false">
<param name="ShowDisplay" value="false">
<param name="ShowStatusBar" value="false">
<param name="AutoSize" value="true">
<embed src="%s" AutoStart="true" ShowTracker="true" ShowControls="true" ShowGotoBar="false" ShowDisplay="false" ShowStatusBar="false" AutoSize="true" pluginspage="http://www.microsoft.com/windows/windowsmedia/download/"></object></p>
</body>
</html>
"""

# HTML template for displaying a QuickTime.mov movie file:
QTMovieTemplate = """<html>
<head>
</head>
<body>
<p><object classid="clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B" codebase="http://www.apple.com/qtactivex/qtplugin.cab" width="100%%" height="100%%">
<param name="src" value="file:///%s">
<param name="scale" value="aspect">
<param name="autoplay" value="true">
<param name="loop" value="false">
<param name="controller" value="true">
<embed src="file:///%s" width="100%%" height="100%%" scale="aspect" autoplay="true" loop="false" controller="true" pluginspage="http://www.apple.com/quicktime/download"></object></p>
</body>
</html>
"""

# HTML template for displaying an image file:
ImageTemplate = """<html>
<head>
</head>
<body>
<img src="%s">
</body>
</html>
"""

# HTML template for playing an MP3 audio file:
MP3Template = """<html>
<head>
<bgsound src="%s">
</head>
<body>
<p>&nbsp;</p>
</body>
</html>
"""

#-------------------------------------------------------------------------------
#  Returns the contents of a specified text file (or None):
#-------------------------------------------------------------------------------

def read_file ( path, mode = 'rb' ):
    """ Returns the contents of a specified text file (or None).
        """
    fh = result = None

    try:
        fh     = file( path, mode )
        result = fh.read()
    except:
        pass

    if fh is not None:
        try:
            fh.close()
        except:
            pass

    return result

#-------------------------------------------------------------------------------
#  Creates a title from a specified string:
#-------------------------------------------------------------------------------

def title_for ( title ):
    """ Creates a title from a specified string.
    """
    return capwords( title.replace( '_', ' ' ) )

#-------------------------------------------------------------------------------
#  Returns a relative CSS style sheet path for a specified path and parent
#  section:
#-------------------------------------------------------------------------------

def css_path_for ( path, parent ):
    """ Returns a relative CSS style sheet path for a specified path and parent
        section.
    """
    if os.path.isfile( os.path.join( path, 'default.css' ) ):
        return 'default.css'

    if parent is not None:
        result = parent.css_path
        if result != '':
            if path != parent.path:
                result = os.path.join( '..', result )

            return result

    return ''

#-------------------------------------------------------------------------------
#  'StdOut' class:
#-------------------------------------------------------------------------------

class StdOut ( object ):
    """ Simulate stdout, but redirect the output to the 'output' string
        supplied by some 'owner' object.
    """

    def __init__ ( self, owner ):
        self.owner = owner

    def write ( self, data ):
        """ Adds the specified data to the output log.
        """
        self.owner.output += data

    def flush ( self ):
        """ Flushes all current data to the output log.
        """
        pass

#-------------------------------------------------------------------------------
#  'NoDemo' class:
#-------------------------------------------------------------------------------

class NoDemo ( HasPrivateTraits ):

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        Heading( 'No demo defined for this lab.' ),
        resizable = True
    )

#-------------------------------------------------------------------------------
#  'DemoPane' class:
#-------------------------------------------------------------------------------

class DemoPane ( HasPrivateTraits ):
    """ Displays the contents of a Python lab's *demo* value.
    """

    #-- Trait Definitions ------------------------------------------------------

    demo = Instance( HasTraits, factory = NoDemo )

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        Item( 'demo',
              id         = 'demo',
              show_label = False,
              style      = 'custom',
              resizable  = True
        ),
        id        = 'enthought.tutor.demo',
        resizable = True
    )

#-------------------------------------------------------------------------------
#  'ATutorialItem' class:
#-------------------------------------------------------------------------------

class ATutorialItem ( HasPrivateTraits ):
    """ Defines the abstract base class for each type of item (HTML, Flash,
        text, code) displayed within the tutor.
    """

    #-- Traits Definitions -----------------------------------------------------

    # The title for the item:
    title = Str

    # The path to the item:
    path = File

    # The displayable content for the item:
    content = Property

#-------------------------------------------------------------------------------
#  'ADescriptionItem' class:
#-------------------------------------------------------------------------------

class ADescriptionItem ( ATutorialItem ):
    """ Defines a common base class for all description items.
    """

    #-- Event Handlers ---------------------------------------------------------

    def _path_changed ( self, path ):
        """ Sets the title for the item based on the item's path name.
        """
        self.title = title_for( os.path.splitext( os.path.basename(
                                                  path ) )[0] )

#-------------------------------------------------------------------------------
#  'HTMLItem' class:
#-------------------------------------------------------------------------------

class HTMLItem ( ADescriptionItem ):
    """ Defines a class used for displaying a single HTML page within the tutor
        using the default Traits HTML editor.
    """

    #-- Traits Definitions -----------------------------------------------------

    url = Str

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        Item( 'content',
              style      = 'readonly',
              show_label = False,
              editor     = HTMLEditor()
        )
    )

    #-- Event Handlers ---------------------------------------------------------

    def _url_changed ( self, url ):
        """ Sets the item title when the 'url' is changed.
        """
        match = url_pat1.match( url )
        if match is not None:
            title = match.group(2).strip()
        else:
            title = url.strip()
            col   = title.rfind( '/' )
            if col >= 0:
                title = os.path.splitext( title[ col + 1: ] )[0]

        self.title = title

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_content ( self ):
        """ Returns the item content.
        """
        url = self.url
        if url != '':
            match = url_pat1.match( url )
            if match is not None:
                url = match.group(1) + match.group(3)

            return url

        return read_file( self.path )

    def _set_content ( self, content ):
        """ Sets the item content.
        """
        self._content = content

#-------------------------------------------------------------------------------
#  'HTMLStrItem' class:
#-------------------------------------------------------------------------------

class HTMLStrItem ( HTMLItem ):
    """ Defines a class used for displaying a single HTML text string within
        the tutor using the default Traits HTML editor.
    """

    # Make the content a real trait rather than a property:
    content = Str

#-------------------------------------------------------------------------------
#  'IEHTMLItem' class:
#-------------------------------------------------------------------------------

class IEHTMLItem ( HTMLItem ):
    """ Defines a class used for displaying a single HTML page within the tutor
        using the Traits Internet Explorer HTML editor.
    """

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        Item( 'content',
              style      = 'readonly',
              show_label = False,
              editor     = IEHTMLEditor()
        )
    )

#-------------------------------------------------------------------------------
#  'IEHTMLStrItem' class:
#-------------------------------------------------------------------------------

class IEHTMLStrItem ( IEHTMLItem ):
    """ Defines a class used for displaying a single HTML text string within
        the tutor using the Traits Internet Explorer HTML editor.
    """

    # Make the content a real trait rather than a property:
    content = Str

#-------------------------------------------------------------------------------
#  'FlashItem' class:
#-------------------------------------------------------------------------------

class FlashItem ( HTMLItem ):
    """ Defines a class used for displaying a Flash-based animation or video
        within the tutor.
    """

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        Item( 'content',
              style      = 'readonly',
              show_label = False,
              editor     = FlashEditor()
        )
    )

#-------------------------------------------------------------------------------
#  'TextItem' class:
#-------------------------------------------------------------------------------

class TextItem ( ADescriptionItem ):
    """ Defines a class used for displaying a text file within the tutor.
    """

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        Item( 'content',
              style      = 'readonly',
              show_label = False,
              editor     = CodeEditor( show_line_numbers = False,
                                       selected_color    = 0xFFFFFF )
        )
    )

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_content ( self ):
        """ Returns the item content.
        """
        return read_file( self.path )

#-------------------------------------------------------------------------------
#  'TextStrItem' class:
#-------------------------------------------------------------------------------

class TextStrItem ( TextItem ):
    """ Defines a class used for displaying a text file within the tutor.
    """

    # Make the content a real trait, rather than a property:
    content = Str

#-------------------------------------------------------------------------------
#  'CodeItem' class:
#-------------------------------------------------------------------------------

class CodeItem ( ATutorialItem ):
    """ Defines a class used for displaying a Python source code fragment
        within the tutor.
    """

    #-- Trait Definitions ------------------------------------------------------

    # The displayable content for the item (override):
    content = Str

    # The starting line of the code snippet within the original file:
    start_line = Int

    # The currently selected line:
    selected_line = Int

    # Should this section normally be hidden?
    hidden = Bool

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        Item( 'content',
              style      = 'custom',
              show_label = False,
              editor     = CodeEditor( selected_line = 'selected_line' )
        )
    )

#-------------------------------------------------------------------------------
#  'ASection' abstract base class:
#-------------------------------------------------------------------------------

class ASection ( HasPrivateTraits ):
    """ Defines an abstract base class for a single section of a tutorial.
    """

    #-- Traits Definitions -----------------------------------------------------

    # The title of the section:
    title = Str

    # The path to this section:
    path = Directory

    # The parent section of this section (if any):
    parent = Instance( 'ASection' )

    # Optional table of contents (can be used to define/locate the subsections):
    toc = List( Str )

    # The path to the CSS style sheet to use for this section:
    css_path = Property

    # The list of subsections contained in this section:
    subsections = Property # List( ASection )

    # This section can be executed:
    is_runnable = Bool( True )

    # Should the Python code be automatically executed on start-up?
    auto_run = Bool( False )

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_subsections ( self ):
        """ Returns the subsections for this section:
        """
        if len( self.toc ) > 0:
            self._load_toc()
        else:
            self._load_dirs()

        # Return the cached list of sections:
        return self._subsections

    @cached_property
    def _get_css_path ( self ):
        """ Returns the path to the CSS style sheet for this section.
        """
        return css_path_for( self.path, self.parent )

    #-- Private Methods --------------------------------------------------------

    def _load_dirs ( self ):
        """ Defines the section's subsections by analyzing all of the section's
            sub-directories.
        """
        # No value cached yet:
        dirs = []
        path = self.path

        # Find every sub-directory whose name begins with a number of the
        # form ddd, or ends with a number of the form _ddd.ddd (used for
        # sorting them into the correct presentation order):
        for name in os.listdir( path ):
            dir = os.path.join( path, name )
            if os.path.isdir( dir ):
               match = dir_pat1.match( name )
               if match is not None:
                   dirs.append( ( float( match.group(1) ),
                                  match.group(2), dir ) )
               else:
                   match = dir_pat2.match( name )
                   if match is not None:
                       dirs.append( ( float( match.group(2) ),
                                      match.group(1), dir ) )

        # Sort the directories by their index value:
        dirs.sort( lambda l, r: cmp( l[0], r[0] ) )

        # Create the appropriate type of section for each valid directory:
        self._subsections = [
            sf.section for sf in [
                SectionFactory( title  = title_for( title ),
                                parent = self ).trait_set(
                                path   = dir )
                for index, title, dir in dirs
            ] if sf.section is not None
        ]

    def _load_toc ( self ):
        """ Defines the section's subsections by finding matches for the items
            defined in the section's table of contents.
        """
        toc         = self.toc
        base_names  = [ item.split( ':', 1 )[0] for item in toc ]
        subsections = [ None ] * len( base_names )
        path        = self.path

        # Classify all file names that match a base name in the table of
        # contents:
        for name in os.listdir( path ):
            try:
                base_name = os.path.splitext( os.path.basename( name ) )[0]
                index     = base_names.index( base_name )
                if subsections[ index ] is None:
                    subsections[ index ] = []
                subsections[ index ].append( name )
            except:
                pass

        # Try to convert each group of names into a section:
        for i, names in enumerate( subsections ):

            # Only process items for which we found at least one matching file
            # name:
            if names is not None:

                # Get the title for the section from its table of contents
                # entry:
                parts = toc[i].split( ':', 1 )
                if len( parts ) == 1:
                    title = title_for( parts[0].strip() )
                else:
                    title = parts[1].strip()

                # Handle an item with one file which is a directory as a normal
                # section:
                if len( names ) == 1:
                    dir = os.path.join( path, names[0] )
                    if os.path.isdir( dir ):
                        factory = SectionFactory(title=title, parent=self)
                        subsections[i] = factory.trait_set(path=dir).section
                        continue

                # Otherwise, create a section from the list of matching files:
                factory = SectionFactory(title=title, parent=self, files=names)
                subsections[i] = factory.trait_set(path=path).section

        # Set the subsections to the non-None values that are left:
        self._subsections = [ subsection for subsection in subsections
                                         if subsection is not None ]

#-------------------------------------------------------------------------------
#  'Lecture' class:
#-------------------------------------------------------------------------------

class Lecture ( ASection ):
    """ Defines a lecture, which is a section of a tutorial with descriptive
        information, but no associated Python code. Can be used to provide
        course overviews, introductory sections, or lead-ins to follow-on
        lessons or labs.
    """

    #-- Trait Definitions-------------------------------------------------------

    # The list of descriptive items for the lecture:
    descriptions = List( ATutorialItem )

    # This section can be executed (override):
    is_runnable = False

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        Item( 'descriptions',
              style      = 'custom',
              show_label = False,
              editor     = list_editor
        ),
        id = 'enthought.tutor.lecture'
    )

#-------------------------------------------------------------------------------
#  'LabHandler' class:
#-------------------------------------------------------------------------------

class LabHandler ( Handler ):
    """ Defines the controller functions for the Lab view.
    """

    def init ( self, info ):
        """ Handles initialization of the view.
        """
        # Run the associated Python code if the 'auto-run' feature is enabled:
        if info.object.auto_run:
            info.object.run_code()

#-------------------------------------------------------------------------------
#  'Lab' class:
#-------------------------------------------------------------------------------

class Lab ( ASection ):
    """ Defines a lab, which is a section of a tutorial with only Python code.
        This type of section might typically follow a lecture which introduced
        the code being worked on in the lab.
    """

    #-- Trait Definitions-------------------------------------------------------

    # The set-up code (if any) for the lab:
    setup = Instance( CodeItem )

    # The list of code items for the lab:
    snippets = List( CodeItem )

    # The list of visible code items for the lab:
    visible_snippets = Property( depends_on = 'visible', cached = True )

    # The currently selected snippet:
    snippet = Instance( CodeItem )

    # Should normally hidden code items be shown?
    visible = Bool( False )

    # The dictionary containing the items from the Python code execution:
    values = Dict #Any( {} )

    # The run Python code button:
    run = Button( image = ImageResource( 'run' ), height_padding = 1 )

    # User error message:
    message = Str

    # The output produced while the program is running:
    output = Str

    # The current demo pane (if any):
    demo = Instance( DemoPane, () )

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        VSplit(
            VGroup(
                Item( 'visible_snippets',
                      style      = 'custom',
                      show_label = False,
                      editor     = snippet_editor
                ),
                HGroup(
                    Item( 'run',
                          style      = 'custom',
                          show_label = False,
                          tooltip    = 'Run the Python code'
                    ),
                    '_',
                    Item( 'message',
                          springy    = True,
                          show_label = False,
                          editor     = TitleEditor()
                    ),
                    '_',
                    Item( 'visible',
                          label = 'View hidden sections'
                    )
                ),
            ),
            Tabbed(
                Item( 'values',
                      id     = 'values_1',
                      label  = 'Shell',
                      editor = ShellEditor( share = True ),
                      dock   = 'tab',
                      export = 'DockWindowShell'
                ),
                Item( 'values',
                      id     = 'values_2',
                      editor = ValueEditor(),
                      dock   = 'tab',
                      export = 'DockWindowShell'
                ),
                Item( 'output',
                      style  = 'readonly',
                      editor = CodeEditor( show_line_numbers = False,
                                           selected_color    = 0xFFFFFF ),
                      dock   = 'tab',
                      export = 'DockWindowShell'
                ),
                Item( 'demo',
                      id        = 'demo',
                      style     = 'custom',
                      resizable = True,
                      dock      = 'tab',
                      export    = 'DockWindowShell'
                ),
                show_labels = False,
            ),
            id = 'splitter',
        ),
        id      = 'enthought.tutor.lab',
        handler = LabHandler
    )

    #-- Event Handlers ---------------------------------------------------------

    def _run_changed ( self ):
        """ Runs the current set of snippet code.
        """
        self.run_code()

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_visible_snippets ( self ):
        """ Returns the list of code items that are currently visible.
        """
        if self.visible:
            return self.snippets

        return [ snippet for snippet in self.snippets if (not snippet.hidden) ]

    #-- Public Methods ---------------------------------------------------------

    def run_code ( self ):
        """ Runs all of the code snippets associated with the section.
        """
        # Reconstruct the lab code from the current set of code snippets:
        start_line = 1
        module     = ''
        for snippet in self.snippets:
            snippet.start_line = start_line
            module      = '%s\n\n%s' % ( module, snippet.content )
            start_line += (snippet.content.count( '\n' ) + 2)

        # Reset any syntax error and message log values:
        self.message   = self.output = ''

        # Redirect standard out and error to the message log:
        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout     = sys.stderr = StdOut( self )

        try:
            try:
                # Get the execution context dictionary:
                values = self.values

                # Clear out any special variables defined by the last run:
                for name in ( 'demo', 'popup' ):
                    if isinstance( values.get( name ), HasTraits ):
                        del values[ name ]

                # Execute the current lab code:
                exec module[2:] in values, values

                # fixme: Hack trying to update the Traits UI view of the dict.
                self.values = {}
                self.values = values

                # Handle a 'demo' value being defined:
                demo = values.get( 'demo' )
                if not isinstance( demo, HasTraits ):
                    demo = NoDemo()
                self.demo.demo = demo

                # Handle a 'popup' value being defined:
                popup = values.get( 'popup' )
                if isinstance( popup, HasTraits ):
                    popup.edit_traits( kind = 'livemodal' )

            except SyntaxError, excp:
                # Convert the line number of the syntax error from one in the
                # composite module to one in the appropriate code snippet:
                line = excp.lineno
                if line is not None:
                    snippet = self.snippets[0]
                    for s in self.snippets:
                        if s.start_line > line:
                            break
                        snippet = s
                    line -= (snippet.start_line - 1)

                    # Highlight the line in error:
                    snippet.selected_line = line

                    # Select the correct code snippet:
                    self.snippet = snippet

                    # Display the syntax error message:
                    self.message = '%s in column %s of line %s' % (
                                   excp.msg.capitalize(), excp.offset, line )
                else:
                    # Display the syntax error message without line # info:
                    self.message = excp.msg.capitalize()
            except:
                import traceback
                traceback.print_exc()
        finally:
            # Restore standard out and error to their original values:
            sys.stdout, sys.stderr = stdout, stderr

#-------------------------------------------------------------------------------
#  'Lesson' class:
#-------------------------------------------------------------------------------

class Lesson ( Lab ):
    """ Defines a lesson, which is a section of a tutorial with both descriptive
        information and associated Python code.
    """

    #-- Trait Definitions-------------------------------------------------------

    # The list of descriptive items for the lesson:
    descriptions = List( ATutorialItem )

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        HSplit(
            Item( 'descriptions',
                  label      = 'Lesson',
                  style      = 'custom',
                  show_label = False,
                  dock       = 'horizontal',
                  editor     = list_editor
            ),
            VSplit(
                VGroup(
                    Item( 'visible_snippets',
                          style      = 'custom',
                          show_label = False,
                          editor     = snippet_editor
                    ),
                    HGroup(
                        Item( 'run',
                              style      = 'custom',
                              show_label = False,
                              tooltip    = 'Run the Python code'
                        ),
                        '_',
                        Item( 'message',
                              springy    = True,
                              show_label = False,
                              editor     = TitleEditor()
                        ),
                        '_',
                        Item( 'visible',
                              label = 'View hidden sections'
                        )
                    ),
                    label = 'Lab',
                    dock  = 'horizontal'
                ),
                Tabbed(
                    Item( 'values',
                          id     = 'values_1',
                          label  = 'Shell',
                          editor = ShellEditor( share = True ),
                          dock   = 'tab',
                          export = 'DockWindowShell'

                    ),
                    Item( 'values',
                          id     = 'values_2',
                          editor = ValueEditor(),
                          dock   = 'tab',
                          export = 'DockWindowShell'
                    ),
                    Item( 'output',
                          style  = 'readonly',
                          editor = CodeEditor( show_line_numbers = False,
                                               selected_color    = 0xFFFFFF ),
                          dock   = 'tab',
                          export = 'DockWindowShell'
                    ),
                    Item( 'demo',
                          id        = 'demo',
                          style     = 'custom',
                          resizable = True,
                          dock      = 'tab',
                          export    = 'DockWindowShell'
                    ),
                    show_labels = False,
                ),
                label = 'Lab',
                dock  = 'horizontal'
            ),
            id = 'splitter',
        ),
        id      = 'enthought.tutor.lesson',
        handler = LabHandler
    )

#-------------------------------------------------------------------------------
#  'Demo' class:
#-------------------------------------------------------------------------------

class Demo ( Lesson ):
    """ Defines a demo, which is a section of a tutorial with both descriptive
        information and associated Python code which is executed but not
        shown.
    """

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        HSplit(
            Item( 'descriptions',
                  label      = 'Lesson',
                  style      = 'custom',
                  show_label = False,
                  dock       = 'horizontal',
                  editor     = list_editor
            ),
            Item( 'demo',
                  id         = 'demo',
                  style      = 'custom',
                  show_label = False,
                  resizable  = True,
                  dock       = 'horizontal',
                  export     = 'DockWindowShell'
            ),
            id = 'splitter',
        ),
        id      = 'enthought.tutor.demo',
        handler = LabHandler
    )

#-------------------------------------------------------------------------------
#  'SectionFactory' class:
#-------------------------------------------------------------------------------

class SectionFactory ( HasPrivateTraits ):
    """ Defines a class that creates Lecture, Lesson or Lab sections (or None),
        based on the content of a specified directory. None is returned if the
        directory does not contain any recognized files.
    """

    #-- Traits Definitions -----------------------------------------------------

    # The path the section is to be created for:
    path = Directory

    # The list of files contained in the section:
    files = List( Str )

    # The parent of the section being created:
    parent = Instance( ASection )

    # The section created from the path:
    section = Instance( ASection )

    # The title for the section:
    title = Str

    # The optional table of contents for the section:
    toc = List( Str )

    # The list of descriptive items for the section:
    descriptions = List( ADescriptionItem )

    # The list of code snippet items for the section:
    snippets = List( CodeItem )

    # The path to the CSS style sheet for the section:
    css_path = Property

    # Should the Python code be automatically executed on start-up?
    auto_run = Bool( False )

    #-- Event Handlers ---------------------------------------------------------

    def _path_changed ( self, path ):
        """ Creates the appropriate section based on the value of the path.
        """
        # Get the list of files to process:
        files = self.files
        if len( files ) == 0:
            # If none were specified, then use all files in the directory:
            files = os.listdir( path )

            # Process the description file (if any) first:
            for name in files:
                if os.path.splitext( name )[1] == '.desc':
                    self._add_desc_item( os.path.join( path, name ) )
                    break

        # Try to convert each file into one or more 'xxxItem' objects:
        toc = [ item.split( ':', 1 )[0].strip() for item in self.toc ]
        for name in files:
            file_name = os.path.join( path, name )

            # Only process the ones that are actual files:
            if os.path.isfile( file_name ):

                # Use the file extension to determine the file's type:
                root, ext = os.path.splitext( name )
                if (root not in toc) and (len( ext ) > 1):

                    # If we have a handler for the file type, invoke it:
                    method = getattr( self, '_add_%s_item' % ext[1:].lower(),
                                      None )
                    if method is not None:
                        method( file_name )

        # Based on the type of items created (if any), create the corresponding
        # type of section:
        if len( self.descriptions ) > 0:
            if len( self.snippets ) > 0:
                if len( [ snippet for snippet in self.snippets
                                  if (not snippet.hidden) ] ) > 0:
                    self.section = Lesson(
                        title        = self.title,
                        path         = path,
                        toc          = self.toc,
                        parent       = self.parent,
                        descriptions = self.descriptions,
                        snippets     = self.snippets,
                        auto_run     = self.auto_run
                    )
                else:
                    self.section = Demo(
                        title        = self.title,
                        path         = path,
                        toc          = self.toc,
                        parent       = self.parent,
                        descriptions = self.descriptions,
                        snippets     = self.snippets,
                        auto_run     = True
                    )
            else:
                self.section = Lecture(
                    title        = self.title,
                    path         = path,
                    toc          = self.toc,
                    parent       = self.parent,
                    descriptions = self.descriptions
                )
        elif len( self.snippets ) > 0:
            self.section = Lab(
                title    = self.title,
                path     = path,
                toc      = self.toc,
                parent   = self.parent,
                snippets = self.snippets,
                auto_run = self.auto_run
            )
        else:
            # No descriptions or code snippets were found. Create a lecture
            # anyway:
            section = Lecture(
                title  = self.title,
                path   = path,
                toc    = self.toc,
                parent = self.parent
            )

            # If the lecture has subsections, then return the lecture and add
            # a default item containing a description of the subsections of the
            # lecture:
            if len( section.subsections ) > 0:
                self._create_html_item( path = path, content =
                         DefaultLecture % ( '\n'.join(
                             [ '<li>%s</li>' % subsection.title
                               for subsection in section.subsections ] ) ) )
                section.descriptions = self.descriptions
                self.section = section

    #-- Property Implementations -----------------------------------------------

    def _get_css_path ( self ):
        """ Returns the path to the CSS style sheet for the section.
        """
        return css_path_for( self.path, self.parent )

    #-- Factory Methods for Creating Section Items Based on File Type ----------

    def _add_py_item ( self, path ):
        """ Creates the code snippets for a Python source file.
        """
        source = read_file( path )
        if source is not None:
            lines      = source.replace( '\r', '' ).split( '\n' )
            start_line = 0
            title      = 'Prologue'
            type       = IsCode

            for i, line in enumerate( lines ):
                match = section_pat1.match( line )
                if match is not None:
                    next_type = IsCode
                else:
                    match = section_pat2.match( line )
                    if match is not None:
                        next_type = IsHiddenCode
                    else:
                        next_type = IsDescription
                        match     = section_pat3.match( line )

                if match is not None:
                    self._add_snippet( title, path, lines, start_line, i - 1,
                                       type )
                    start_line = i + 1
                    title      = match.group(1).strip()
                    type       = next_type

            self._add_snippet( title, path, lines, start_line, i, type )

    def _add_txt_item ( self, path ):
        """ Creates a description item for a normal text file.
        """
        self.descriptions.append( TextItem( path = path ) )

    def _add_htm_item ( self, path ):
        """ Creates a description item for an HTML file.
        """
        # Check if there is a corresponding .rst (restructured text) file:
        dir, base_name = os.path.split( path )
        rst = os.path.join( dir, os.path.splitext( base_name )[0] + '.rst' )

        # If no .rst file exists, just add the file as a normal HTML file:
        if not os.path.isfile( rst ):
            self._create_html_item( path = path )

    def _add_html_item ( self, path ):
        """ Creates a description item for an HTML file.
        """
        self._add_htm_item( path )

    def _add_url_item ( self, path ):
        """ Creates a description item for a file containing URLs.
        """
        data = read_file( path )
        if data is not None:
            for url in [ line for line in data.split( '\n' )
                              if line.strip()[:1] not in ( '', '#' ) ]:
                self._create_html_item( url = url.strip() )

    def _add_rst_item ( self, path ):
        """ Creates a description item for a ReSTructured text file.
        """
        # If docutils is not installed, just process the file as an ordinary
        # text file:
        try:
            from docutils.core import publish_cmdline
        except:
            self._add_txt_item( path )
            return

        # Get the name of the HTML file we will write to:
        dir, base_name = os.path.split( path )
        html = os.path.join( dir, os.path.splitext( base_name )[0] + '.htm' )

        # Try to find a CSS style sheet, and set up the docutil overrides if
        # found:
        settings = {}
        css_path = self.css_path
        if css_path != '':
            css_path = os.path.join( self.path, css_path )
            settings[ 'stylesheet_path' ]  = css_path
            settings[ 'embed_stylesheet' ] = True
            settings[ 'stylesheet' ]       = None
        else:
            css_path = path

        # If the HTML file does not exist, or is older than the restructured
        # text file, then let docutils convert it to HTML:
        is_file = os.path.isfile( html )
        if ((not is_file) or
            (os.path.getmtime( path )     > os.path.getmtime( html )) or
            (os.path.getmtime( css_path ) > os.path.getmtime( html ))):

            # Delete the current HTML file (if any):
            if is_file:
                os.remove( html )

            # Let docutils create a new HTML file from the restructured text
            # file:
            publish_cmdline( writer_name        = 'html',
                             argv               = [ path, html ],
                             settings_overrides = settings )

        if os.path.isfile( html ):
            # If there is now a valid HTML file, use it:
            self._create_html_item( path = html )

        else:
            # Otherwise, just use the original restructured text file:
            self._add_txt_item( path )

    def _add_swf_item ( self, path ):
        """ Creates a description item for a Flash file.
        """
        if is_windows:
            self.descriptions.append( FlashItem( path = path ) )

    def _add_mov_item ( self, path ):
        """ Creates a description item for a QuickTime movie file.
        """
        path2 = path.replace( ':', '|' )
        self._create_html_item( path    = path,
                                content = QTMovieTemplate % ( path2, path2 ) )

    def _add_wmv_item ( self, path ):
        """ Creates a description item for a Windows movie file.
        """
        self._create_html_item( path    = path,
                                content = WMVMovieTemplate % ( path, path ) )

    def _add_avi_item ( self, path ):
        """ Creates a description item for an AVI movie file.
        """
        self._add_wmv_item( path )

    def _add_jpg_item ( self, path ):
        """ Creates a description item for a JPEG image file.
        """
        self._create_html_item( path    = path,
                                content = ImageTemplate % path )

    def _add_jpeg_item ( self, path ):
        """ Creates a description item for a JPEG image file.
        """
        self._add_jpg_item( path )

    def _add_png_item ( self, path ):
        """ Creates a description item for a PNG image file.
        """
        self._add_jpg_item( path )

    def _add_mp3_item ( self, path ):
        """ Creates a description item for an mp3 audio file.
        """
        self._create_html_item( path    = path,
                                content = MP3Template % path )

    def _add_desc_item ( self, path ):
        """ Creates a section title from a description file.
        """
        # If we've already processed a description file, then we're done:
        if len( self.toc ) > 0:
            return

        lines = []
        desc  = read_file( path )
        if desc is not None:
            # Split the file into lines and save the non-empty, non-comment
            # lines:
            for line in desc.split( '\n' ):
                line = line.strip()
                if (len( line ) > 0) and (line[0] != '#'):
                    lines.append( line )

        if len( lines ) == 0:
            # If the file didn't have anything useful in it, set a title based
            # on the description file name:
            self.title = title_for(
                             os.path.splitext( os.path.basename( path ) )[0] )
        else:
            # Otherwise, set the title and table of contents from the lines in
            # the file:
            self.title = lines[0]
            self.toc   = lines[1:]

    #-- Private Methods --------------------------------------------------------

    def _add_snippet ( self, title, path, lines, start_line, end_line, type ):
        """ Adds a new code snippet or restructured text item to the list of
            code snippet or description items.
        """
        # Trim leading and trailing blank lines from the snippet:
        while start_line <= end_line:
            if lines[ start_line ].strip() != '':
                break
            start_line += 1

        while end_line >= start_line:
            if lines[ end_line ].strip() != '':
                break
            end_line -= 1

        # Only add if the snippet is not empty:
        if start_line <= end_line:

            # Check for the title containing the 'auto-run' flag ('*'):
            if title[:1] == '*':
                self.auto_run = True
                title = title[1:].strip()

            if title[-1:] == '*':
                self.auto_run = True
                title = title[:-1].strip()

            # Extract out just the lines we will use:
            content_lines = lines[ start_line: end_line + 1 ]

            if type == IsDescription:
                # Add the new restructured text description:
                self._add_description( content_lines, title )
            else:
                # Add the new code snippet:
                self.snippets.append( CodeItem(
                    title   = title or 'Code',
                    path    = path,
                    hidden  = (type == IsHiddenCode),
                    content = '\n'.join( content_lines )
                ) )

    def _add_description ( self, lines, title ):
        """ Converts a restructured text string to HTML and adds it as
            description item.
        """
        # Scan the lines for any imbedded Python code that should be shown as
        # a separate snippet:
        i = 0
        while i < len( lines ):
            if lines[i].strip()[-2:] == '::':
                i = self._check_embedded_code( lines, i + 1 )
            else:
                i += 1

        # Strip off any docstring style triple quotes (if necessary):
        content = '\n'.join( lines ).strip()
        if content[:3] in ( '"""', "'''" ):
            content = content[3:]

        if content[-3:] in ( '"""', "'''" ):
            content = content[:-3]

        content = content.strip()

        # If docutils is not installed, just add it as a text string item:
        try:
            from docutils.core import publish_string
        except:
            self.descriptions.append( TextStrItem( content = content,
                                                   title   = title ) )
            return

        # Try to find a CSS style sheet, and set up the docutil overrides if
        # found:
        settings = {}
        css_path = self.css_path
        if css_path != '':
            css_path = os.path.join( self.path, css_path )
            settings[ 'stylesheet_path' ]  = css_path
            settings[ 'embed_stylesheet' ] = True
            settings[ 'stylesheet' ]       = None

        # Convert it from restructured text to HTML:
        html = publish_string( content, writer_name        = 'html',
                                        settings_overrides = settings )

        # Choose the right HTML renderer:
        if is_windows:
            item = IEHTMLStrItem( content = html, title = title )
        else:
            item = HTMLStrItem( content = html, title = title )

        # Add the resulting item to the descriptions list:
        self.descriptions.append( item )

    def _create_html_item ( self, **traits ):
        """ Creates a platform specific html item and adds it to the list of
            descriptions.
        """
        if is_windows:
            item = IEHTMLItem( **traits )
        else:
            item = HTMLItem( **traits )

        self.descriptions.append( item )

    def _check_embedded_code ( self, lines, start ):
        """ Checks for an embedded Python code snippet within a description.
        """
        n = len( lines )
        while start < n:
            line = lines[ start ].strip()

            if line == '':
                start += 1
                continue

            if (line[:1] != '[') or (line[-1:] != ']'):
                break

            del lines[ start ]

            n     -= 1
            title  = line[1:-1].strip()
            line   = lines[ start ] + '.'
            pad    = len( line ) - len( line.strip() )
            clines = []

            while start < n:
                line     = lines[ start ] + '.'
                len_line = len( line.strip() )
                if (len_line > 1) and ((len( line ) - len_line) < pad):
                    break

                if (len( clines ) > 0) or (len_line > 1):
                    clines.append( line[ pad: -1 ] )

                start += 1

            # Add the new code snippet:
            self.snippets.append( CodeItem(
                title   = title or 'Code',
                content = '\n'.join( clines )
            ) )

            break

        return start

#-------------------------------------------------------------------------------
#  Tutor tree editor:
#-------------------------------------------------------------------------------

tree_editor = TreeEditor(
    nodes = [
        TreeNode(
            children   = 'subsections',
            label      = 'title',
            rename     = False,
            copy       = False,
            delete     = False,
            delete_me  = False,
            insert     = False,
            auto_open  = True,
            auto_close = False,
            node_for   = [ ASection ],
            icon_group = '<group>'
        )
    ],
    editable  = False,
    auto_open = 1,
    selected = 'section'
)

#-------------------------------------------------------------------------------
#  'Tutor' class:
#-------------------------------------------------------------------------------

class Tutor ( HasPrivateTraits ):
    """ The main tutorial class which manages the presentation and navigation
        of the entire tutorial.
    """

    #-- Trait Definitions ------------------------------------------------------

    # The path to the files distributed with the tutor:
    home = Directory

    # The path to the root of the tutorial tree:
    path = Directory

    # The root of the tutorial lesson tree:
    root = Instance( ASection )

    # The current section of the tutorial being displayed:
    section = Instance( ASection )

    # The next section:
    next_section = Property( depends_on = 'section', cached = True )

    # The previous section:
    previous_section = Property( depends_on = 'section', cached = True )

    # The previous section button:
    previous = Button( image = ImageResource( 'previous' ), height_padding = 1 )

    # The next section button:
    next = Button( image = ImageResource( 'next' ), height_padding = 1 )

    # The parent section button:
    parent = Button( image = ImageResource( 'parent' ), height_padding = 1 )

    # The reload tutor button:
    reload = Button( image = ImageResource( 'reload' ), height_padding = 1 )

    # The title of the current session:
    title = Property( depends_on = 'section' )

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        VGroup(
            HGroup(
                Item( 'previous',
                      style        = 'custom',
                      enabled_when = 'previous_section is not None',
                      tooltip      = 'Go to previous section'
                ),
                Item( 'parent',
                      style        = 'custom',
                      enabled_when = '(section is not None) and '
                                     '(section.parent is not None)',
                      tooltip      = 'Go up one level'
                ),
                Item( 'next',
                      style        = 'custom',
                      enabled_when = 'next_section is not None',
                      tooltip      = 'Go to next section'
                ),
                '_',
                Item( 'title',
                      springy = True,
                      editor  = TitleEditor()
                ),
                '_',
                Item( 'reload',
                      style   = 'custom',
                      tooltip = 'Reload the tutorial'
                ),
                show_labels = False
            ),
            '_',
            HSplit(
                Item( 'root',
                      label  = 'Table of Contents',
                      editor = tree_editor,
                      dock   = 'horizontal',
                      export = 'DockWindowShell'
                ),
                Item( 'section',
                      id        = 'section',
                      label     = 'Current Lesson',
                      style     = 'custom',
                      resizable = True,
                      dock      = 'horizontal'
                ),
                id          = 'splitter',
                show_labels = False
            )
        ),
        title     = 'Python Tutor',
        id        = 'dmorrill.tutor.tutor:1.0',
        buttons   = NoButtons,
        resizable = True,
        width     = 0.8,
        height    = 0.8
    )

    #-- Event Handlers ---------------------------------------------------------

    def _path_changed ( self, path ):
        """ Handles the tutorial root path being changed.
        """
        self.init_tutor()

    def _next_changed ( self ):
        """ Displays the next tutorial section.
        """
        self.section = self.next_section

    def _previous_changed ( self ):
        """ Displays the previous tutorial section.
        """
        self.section = self.previous_section

    def _parent_changed ( self ):
        """ Displays the parent of the current tutorial section.
        """
        self.section = self.section.parent

    def _reload_changed ( self ):
        """ Reloads the tutor from the original path specified.
        """
        self.init_tutor()

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_next_section ( self ):
        """ Returns the next section of the tutorial.
        """
        next    = None
        section = self.section
        if len( section.subsections ) > 0:
            next = section.subsections[0]
        else:
            parent = section.parent
            while parent is not None:
                index = parent.subsections.index( section )
                if index < (len( parent.subsections ) - 1):
                    next = parent.subsections[ index + 1 ]
                    break

                parent, section = parent.parent, parent

        return next

    @cached_property
    def _get_previous_section ( self ):
        """ Returns the previous section of the tutorial.
        """
        previous = None
        section  = self.section
        parent   = section.parent
        if parent is not None:
            index = parent.subsections.index( section )
            if index > 0:
                previous = parent.subsections[ index - 1 ]
                while len( previous.subsections ) > 0:
                    previous = previous.subsections[-1]
            else:
                previous = parent

        return previous

    def _get_title ( self ):
        """ Returns the title of the current section.
        """
        section = self.section
        if section is None:
            return ''

        return ('%s: %s' % ( section.__class__.__name__, section.title ))

    #-- Public Methods ---------------------------------------------------------

    def init_tutor ( self ):
        """ Initials the tutor by creating the root section from the specified
            path.
        """
        path    = self.path
        title   = title_for( os.path.splitext( os.path.basename( path ) )[0] )
        section = SectionFactory(title=title).trait_set(path=path).section
        if section is not None:
            self.section = self.root = section

#-------------------------------------------------------------------------------
#  Run the program:
#-------------------------------------------------------------------------------

# Only run the program if we were invoked from the command line:
if __name__ == '__main__':

    # Validate the command line arguments:
    if len( sys.argv ) > 2:
        print Usage
        sys.exit( 1 )

    # Determine the root path to use for the tutorial files:
    if len( sys.argv ) == 2:
        path = sys.argv[1]
    else:
        path = os.getcwd()

    # Create a tutor and display the tutorial:
    tutor = Tutor( home = os.path.dirname( sys.argv[0] ) ).trait_set(
                   path = path )
    if tutor.root is not None:
        tutor.configure_traits()
    else:
        print """No traits tutorial found in %s.

Correct usage is: python tutor.py [tutorial_path]
where: tutorial_path = Path to the root of the traits tutorial.

If tutorial_path is omitted, the current directory is assumed to be the root of
the tutorial.""" % path
