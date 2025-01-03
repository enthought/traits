# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Utility functions for managing and finding resources (e.g. images, files).

    get_path :           Returns the absolute path of a class or instance

    create_unique_name : Creates a name with a given prefix that is not in a
                         given list of existing names. The separator between
                         the prefix and the rest of the name can also be
                         specified (default is a '_')
"""


# Standard library imports.
import inspect
import os
import sys


def get_path(path):
    """ Returns an absolute path for the specified path.

    'path' can be a string, class or instance.

    """

    if type(path) is not str:
        # Is this a class or an instance?
        if inspect.isclass(path):
            klass = path

        else:
            klass = path.__class__

        # Get the name of the module that the class was loaded from.
        module_name = klass.__module__

        # Look the module up.
        module = sys.modules[module_name]

        if module_name == "__main__":
            dirs = [os.path.dirname(sys.argv[0]), os.getcwd()]
            for d in dirs:
                if os.path.exists(d):
                    path = d
                    break
        else:
            # Get the path to the module.
            path = os.path.dirname(module.__file__)

    return path


def create_unique_name(prefix, names, separator="_"):
    """ Creates a name starting with 'prefix' that is not in 'names'. """

    i = 1

    name = prefix
    while name in names:
        name = prefix + separator + str(i)
        i += 1

    return name
