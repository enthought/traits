#------------------------------------------------------------------------------
# Copyright (c) 2008, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Vibha Srinivasan <vibha@enthought.com>
#------------------------------------------------------------------------------

""" Generates a file containing definitions for the editors defined in the 
various backends.
"""

import os, glob, sys
from enthought.traits.ui.editor import Editor
from enthought.traits.ui.editor_factory import EditorFactory
from toolkit import TraitUIToolkits

def gen_editor_definitions(target_filename):
    """ Generates a file containing definitions for the editors defined in the 
    various backends.
    """

    base_import_path = 'enthought.traits.ui.'
    editor_generators = []
    for toolkit in TraitUIToolkits:
        import_path = base_import_path + toolkit + '.editors'
        try:
           __import__(import_path)
           mod = sys.modules[import_path]
           editor_generators.extend([
              (name, ''.join([item.capitalize() for item in name.split('_')])) 
              for name in dir(mod) if '_editor' in name])
        except Exception, e:
           pass   
    editors = dict(zip(editor_generators, range(len(editor_generators)))).keys()
    target_file = open(target_filename, 'w')
    prelims = \
"""
import sys
from toolkit import toolkit

"""
    target_file.write(prelims)
    for name, class_name in editors:
            function = "def %s(*args, **traits):"%class_name
            target_file.write(function)
            target_file.write('\n')
            func_code = \
    """
    name = toolkit().__module__.rstrip('.toolkit') + '.editors'
    __import__(name)
    """
            target_file.write(func_code)
            target_file.write("return sys.modules[name].%s( *args, **traits )" % name)
            target_file.write('\n\n')  
    target_file.close()   
