#------------------------------------------------------------------------------
# Copyright (c) 2008, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Vibha Srinivasan <vibha@enthought.com>
#------------------------------------------------------------------------------

""" Generates a file containing definitions for editors defined in the various
backends.
"""

import os, glob, sys

def gen_editor_definitions(target_filename = 'editors.py'):
    """ Generates a file containing definitions for editors defined in the 
       various backends.

    The idea is that if a new editor has been declared in any of the backends,
    the author needs to create a file called '***_definition' in the Traits
    package (in enthought.traits.ui). This function will be run each time the
    user runs the setup.py file, and the new editor's definition will be 
    appended to the editors.py file.
 
    The structure of the ***_definition file should be as follows:
    ***_definition = '<file name in the backend package>:
                     <name of the Editor or the EditorFactory class'
    """

    base_import_path = 'enthought.traits.ui.'
    definition_files = glob.glob('*_definition.py')
    new_editors = []
    for file in definition_files:
           import_path = base_import_path + file.rstrip('.py')
           __import__(import_path)
           mod = sys.modules[import_path]
           for name in dir(mod):
               if '_definition' in name:
                   (file_name, class_name) = getattr(mod, name).split(':')
                   new_editors.append((file_name, class_name))
    
    target_file = open(target_filename, 'a')
    for editor_name in new_editors:
            function = "def %s( *args, **traits ):\n" % class_name
            target_file.write(function)
            func_code =  ' '*4 + 'import sys\n'
            func_code += ' '*4 + \
                         'name = toolkit().__module__.rstrip(".toolkit")' + \
                         ' + ".%s"\n' % file_name 
            func_code += ' '*4 + "__import__(name)\n"
            func_code += ' '*4 + \
                         'return sys.modules[name].%s( *args, **traits )' \
                         % class_name
            target_file.write(func_code) 
            target_file.write('\n\n')  
    target_file.close()   
