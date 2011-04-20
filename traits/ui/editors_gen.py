#------------------------------------------------------------------------------
# Copyright (c) 2008, Enthought, Inc.
# All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#
# Author: Vibha Srinivasan <vibha@enthought.com>
#------------------------------------------------------------------------------

""" Generates a file containing definitions for editors defined in the various
backends.
"""

from __future__ import absolute_import

import glob

def gen_editor_definitions(target_filename = 'editors.py'):
    """ Generates a file containing definitions for editors defined in the
       various backends.

    The idea is that if a new editor has been declared in any of the backends,
    the author needs to create a file called '<myeditor>_definition' in the
    Traits package (in enthought.traits.ui). This function will be run each time
    the user runs the setup.py file, and the new editor's definition will be
    appended to the editors.py file.

    The structure of the <myeditor>_definition file should be as follows::

        myeditor_definition = '<file name in the backend package>:
                         <name of the Editor or the EditorFactory class'
    """

    definition_files = glob.glob('*_definition.py')
    new_editors = []
    for file in definition_files:
           import_path = file.rstrip('.py')
           mod = __import__(import_path, globals=globals(), level=1)
           for name in dir(mod):
               if '_definition' in name:
                   new_editors.append(getattr(mod, name))
    target_file = open(target_filename, 'a')
    for editor_name in new_editors:
            function = "\ndef %s( *args, **traits ):\n" % editor_name.split(':')[1]
            target_file.write(function)
            func_code =  ' '*4 + 'from toolkit import toolkit_object\n'
            func_code += ' '*4 + \
                         'return toolkit_object("%s")( *args, **traits )' \
                         % editor_name
            target_file.write(func_code)
            target_file.write('\n\n')
    target_file.close()
