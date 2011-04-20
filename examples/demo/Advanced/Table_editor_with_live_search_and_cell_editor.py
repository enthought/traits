#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
This example demonstrates how to implement 'live search' using a TableEditor,
as well as how to embed more sophisticated editors, such as a CodeEditor, within
a table cell. This example also makes extensive use of cached properties.

The example is a fairly simple source code file search utility. You determine
which files to search and what to search for using the various controls spread
across the top line of the view.

You specify the root directory to search for files in using the 'Path' field.
You can either:

  - Type in a directory name.
  - Click the '...' button and select a directory from the drop-down tree view
    that is displayed.
  - Click on the directory name drop-down to display a history list of the 10
    most recently visited directories, and select a directory from the list.

You can specify whether sub-directories should be included or not by toggling
the 'Recursive' checkbox on or off.

You can specify the types of files to be searched by clicking on the 'Type'
drop-down and selecting a file type such as Python or C from the list.

You can specify what string to search for by typing into the 'Search' field.
The set of source files containing the search string is automatically updated
as you type (this is the 'live search' feature). The search field also maintains
a history of previous searches, so you can click on the drop-down arrow to
display and select a previous search. Note that entries are only added to the
search history when the enter key is pressed. This prevents each partial
substring typed from being added to the history as a separate entry.

You can specify whether the search is case sensitive or not by toggling the
'Case sensitive' checkbox on or off.

The results of the search are displayed in a table below the input fields.
The table contains four columns:

  - #: The number of lines matching the search string in the file.
  - Matches: A list of all lines containing search string matches in the file.
    Normally, only the first match is displayed, but you can click on this
    field to display the entire list of matches (the table row will expand and a
    CodeEditor will be displayed showing the complete list of matching source
    code file lines). You can click on or cursor to lines in the code editor to
    display the corresponding source code line in context in the code editor
    that appears at the bottom of the view.
  - Name: Displays the base name of the source file with no path information.
  - Path: Displays the portion of the source file path not included in the
    the root directory being used for the search.

Selecting a line in the table editor will display the contents of the
corresponding source file in the Code Editor displayed at the bottom of the
view.

After clicking on a 'Matches' column entry you can use the cursor up and down
keys to select the various matching source code lines displayed in the table
cell editor. You can move to the next or previous 'Matches' entry by pressing
the Ctrl-Up and Ctrl-Down cursor keys. You can also use the Ctrl-Left and
Ctrl-Right cursor keys to move to the previous or next column on the same line.

You can also exit the 'Matches' code editor by pressing the Escape key.

Finally:

  - You can click and drag the little circle to the right of the currently
    selected file to drag and drop the file. This can be useful, for example, to
    drag and drop the file into your favorite text editor.

  - Similarly, you can also drag the contents of the 'Name' column into your
    favorite text editor to edit the file corresponding to that line in the
    table.
"""

#-- Imports --------------------------------------------------------------------

from os \
    import walk, getcwd, listdir

from os.path \
    import basename, dirname, splitext, join

from traits.api \
    import HasTraits, File, Directory, Str, Bool, Int, Enum, Instance, \
           Property, Any, property_depends_on

from traitsui.api \
    import View, VGroup, VSplit, HGroup, Item, TableEditor, CodeEditor, \
           TitleEditor, HistoryEditor, DNDEditor

from traitsui.table_column \
    import ObjectColumn

#-- Constants ------------------------------------------------------------------

FileTypes = {
    'Python': [ '.py' ],
    'C':      [ '.c', '.h' ],
    'C++':    [ '.cpp', '.h' ],
    'Java':   [ '.java' ],
    'Ruby':   [ '.rb' ]
}

#-- The Live Search table editor definition ------------------------------------

class MatchesColumn1 ( ObjectColumn ):

    def get_value ( self, object ):
        n = len( self.get_raw_value( object ) )
        if n == 0:
            return ''

        return str( n )

class MatchesColumn2 ( ObjectColumn ):

    def is_editable ( self, object ):
        return (len( object.matches ) > 0)

class FileColumn ( ObjectColumn ):

    def get_drag_value ( self, object ):
        return object.full_name

table_editor = TableEditor(
    columns = [
        MatchesColumn1( name        = 'matches',
                        label       = '#',
                        editable    = False,
                        width       = 0.05,
                        horizontal_alignment = 'center' ),
        MatchesColumn2( name        = 'matches',
                        width       = 0.35,
                        format_func = lambda x: (x + [ '' ])[0].strip(),
                        editor      = CodeEditor( line =
                                          'object.live_search.selected_match',
                                        selected_line =
                                          'object.live_search.selected_match' ),
                        style       = 'readonly',
                        edit_width  = 0.95,
                        edit_height = 0.33 ),
        FileColumn(     name        = 'base_name',
                        label       = 'Name',
                        width       = 0.30,
                        editable    = False ),
        ObjectColumn(   name        = 'ext_path',
                        label       = 'Path',
                        width       = 0.30,
                        editable    = False ),
    ],
    filter_name        = 'filter',
    auto_size          = False,
    show_toolbar       = False,
    selected           = 'selected',
    selection_color    = 0x000000,
    selection_bg_color = 0xFBD391
)

#-- LiveSearch class -----------------------------------------------------------

class LiveSearch ( HasTraits ):

    # The currenty root directory being searched:
    root = Directory( getcwd(), entries = 10 )

    # Should sub directories be included in the search:
    recursive = Bool( True )

    # The file types to include in the search:
    file_type = Enum( 'Python', 'C', 'C++', 'Java', 'Ruby' )

    # The current search string:
    search = Str

    # Is the search case sensitive?
    case_sensitive = Bool( False )

    # The live search table filter:
    filter = Property # Instance( TableFilter )

    # The current list of source files being searched:
    source_files = Property # List( SourceFile )

    # The currently selected source file:
    selected = Any # Instance( SourceFile )

    # The contents of the currently selected source file:
    selected_contents = Property # List( Str )

    # The currently selected match:
    selected_match = Int

    # The text line corresponding to the selected match:
    selected_line = Property # Int

    # The full name of the currently selected source file:
    selected_full_name = Property # File

    # The list of marked lines for the currently selected file:
    mark_lines = Property # List( Int )

    # Summary of current number of files and matches:
    summary = Property # Str

    #-- Traits UI Views --------------------------------------------------------

    view = View(
        VGroup(
            HGroup(
                Item( 'root',
                      id    = 'root',
                      label = 'Path',
                      width = 0.5
                ),
                Item( 'recursive' ),
                Item( 'file_type', label = 'Type' ),
                Item( 'search',
                      id     = 'search',
                      width  = 0.5,
                      editor = HistoryEditor( auto_set = True )
                ),
                Item( 'case_sensitive' )
            ),
            VSplit(
                VGroup(
                    Item( 'summary',
                          editor = TitleEditor()
                    ),
                    Item( 'source_files',
                          id     = 'source_files',
                          editor = table_editor
                    ),
                    dock        = 'horizontal',
                    show_labels = False
                ),
                VGroup(
                    HGroup(
                        Item( 'selected_full_name',
                              editor  = TitleEditor(),
                              springy = True
                        ),
                        Item( 'selected_full_name',
                              editor  = DNDEditor(),
                              tooltip = 'Drag this file'
                        ),
                        show_labels = False
                    ),
                    Item( 'selected_contents',
                          style  = 'readonly',
                          editor = CodeEditor( mark_lines    = 'mark_lines',
                                               line          = 'selected_line',
                                               selected_line = 'selected_line' )
                    ),
                    dock        = 'horizontal',
                    show_labels = False
                ),
                id = 'splitter'
            )
        ),
        title     = 'Live File Search',
        id        = 'enthought.examples.demo.Advanced.'
                    'Table_editor_with_live_search_and_cell_editor.LiveSearch',
        width     = 0.75,
        height    = 0.67,
        resizable = True
    )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'search, case_sensitive' )
    def _get_filter ( self ):
        if len( self.search ) == 0:
            return lambda x: True

        return lambda x: len( x.matches ) > 0

    @property_depends_on( 'root, recursive, file_type' )
    def _get_source_files ( self ):
        root = self.root
        if root == '':
            root = getcwd()

        file_types = FileTypes[ self.file_type ]
        if self.recursive:
            result = []
            for dir_path, dir_names, file_names in walk( root ):
                for file_name in file_names:
                    if splitext( file_name )[1] in file_types:
                        result.append( SourceFile(
                            live_search = self,
                            full_name   = join( dir_path, file_name ) ) )
            return result

        return [ SourceFile( live_search = self,
                             full_name   = join( root, file_name ) )
                 for file_name in listdir( root )
                 if splitext( file_name )[1] in file_types ]

    @property_depends_on( 'selected' )
    def _get_selected_contents ( self ):
        if self.selected is None:
            return ''

        return ''.join( self.selected.contents )

    @property_depends_on( 'selected' )
    def _get_mark_lines ( self ):
        if self.selected is None:
            return []

        return [ int( match.split( ':', 1 )[0] )
                 for match in self.selected.matches ]

    @property_depends_on( 'selected, selected_match' )
    def _get_selected_line ( self ):
        selected = self.selected
        if (selected is None) or (len( selected.matches ) == 0):
            return 1

        return int( selected.matches[ self.selected_match - 1
                                    ].split( ':', 1 )[0] )

    @property_depends_on( 'selected' )
    def _get_selected_full_name ( self ):
        if self.selected is None:
            return ''

        return self.selected.full_name

    @property_depends_on( 'source_files, search, case_sensitive' )
    def _get_summary ( self ):
        source_files = self.source_files
        search       = self.search
        if search == '':
            return 'A total of %d files.' % len( source_files )

        files   = 0
        matches = 0
        for source_file in source_files:
            n = len( source_file.matches )
            if n > 0:
                files   += 1
                matches += n

        return 'A total of %d files with %d files containing %d matches.' % (
               len( source_files ), files, matches )

    #-- Traits Event Handlers --------------------------------------------------

    def _selected_changed ( self ):
        self.selected_match = 1

    def _source_files_changed ( self ):
        if len( self.source_files ) > 0:
            self.selected = self.source_files[0]
        else:
            self.selected = None

#-- SourceFile class -----------------------------------------------------------

class SourceFile ( HasTraits ):

    # The search object this source file is associated with:
    live_search = Instance( LiveSearch )

    # The full path and file name of the source file:
    full_name = File

    # The base file name of the source file:
    base_name = Property # Str

    # The portion of the file path beyond the root search path:
    ext_path = Property # Str

    # The contents of the source file:
    contents = Property # List( Str )

    # The list of matches for the current search criteria:
    matches = Property # List( Str )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'full_name' )
    def _get_base_name ( self ):
        return basename( self.full_name )

    @property_depends_on( 'full_name' )
    def _get_ext_path ( self ):
        return dirname( self.full_name )[ len( self.live_search.root ): ]

    @property_depends_on( 'full_name' )
    def _get_contents ( self ):
        try:
            fh = open( self.full_name, 'rb' )
            contents = fh.readlines()
            fh.close()
            return contents
        except:
            return ''

    @property_depends_on( 'full_name, live_search.[search, case_sensitive]' )
    def _get_matches ( self ):
        search = self.live_search.search
        if search == '':
            return []

        case_sensitive = self.live_search.case_sensitive
        if case_sensitive:
            return [ '%5d: %s' % ( (i + 1), line.strip() )
                     for i, line in enumerate( self.contents )
                     if line.find( search ) >= 0 ]

        search = search.lower()
        return [ '%5d: %s' % ( (i + 1), line.strip() )
                 for i, line in enumerate( self.contents )
                 if line.lower().find( search ) >= 0 ]

#-- Set up and run the demo ----------------------------------------------------

# Create the demo object:
demo = LiveSearch()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

