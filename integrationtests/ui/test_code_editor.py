#-------------------------------------------------------------------------------
#
#  Test using a KeyBindings object with the traits Codeditor
#
#  Written by: David C. Morrill
#
#  Date: 09/22/2005
#
#  (c) Copyright 2005 by Enthought, Inc.
#  License: BSD Style.
#
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import HasPrivateTraits, Code, Str

from traitsui.api \
    import View, Item, Handler, CodeEditor

from traitsui.key_bindings \
    import KeyBinding, KeyBindings

#-------------------------------------------------------------------------------
#  Define a KeyBindings object:
#-------------------------------------------------------------------------------

key_bindings = KeyBindings(

    KeyBinding( binding1    = 'Ctrl-s',
                description = 'Save to a file',
                method_name = 'save_file' ),

    KeyBinding( binding1    = 'Ctrl-r',
                description = 'Run script',
                method_name = 'run_script' ),

    KeyBinding( binding1    = 'Ctrl-q',
                description = 'Edit key bindings',
                method_name = 'edit_bindings' )
)

#-------------------------------------------------------------------------------
#  'CodeHandler' class:
#-------------------------------------------------------------------------------

class CodeHandler ( Handler ):

    def save_file ( self, info ):
        info.object.status = "save file"

    def run_script ( self, info ):
        info.object.status = "run script"

    def edit_bindings ( self, info ):
        info.object.status = "edit bindings"
        key_bindings.edit_traits()

#-------------------------------------------------------------------------------
#  'TestCode' class:
#-------------------------------------------------------------------------------

class TestCode ( HasPrivateTraits ):

    code   = Code
    status = Str

    view = View(
               [ Item( 'code',
                       style     = 'custom',
                       resizable = True,
                       editor    = CodeEditor( key_bindings = key_bindings ) ),
                 'status~',
                 '|<>' ],
               id = 'traitsui.tests.test_code_editor.TestCode',
               title     = 'Sample Code Editor',
               width     = 0.4,
               height    = 0.4,
               resizable = True,
               handler   = CodeHandler() )

#-------------------------------------------------------------------------------
#  Run the test:
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    TestCode().configure_traits()

