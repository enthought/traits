# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

#  fixme:
#  - Get custom tree view images.
#  - Write a program to create a directory structure from a lesson plan file.

""" Script to run the tutorial.
"""


import os
import sys

from traitsui.extras.demo import demo

# Correct program usage information:
usage = """
Correct usage is: tutor.py [root_dir]
where:
    root_dir = Path to root of the tutorial tree

If omitted, 'root_dir' defaults to the current directory."""


def main(root_dir):
    # Create a tutor and display the tutorial:
    path, name = os.path.splitext(root_dir)
    demo(dir_name=root_dir, title='Traits Demos')


if __name__ == "__main__":

    # Validate the command line arguments:
    if len(sys.argv) > 2:
        print(usage)
        sys.exit(1)

    # Determine the root path to use for the tutorial files:
    if len(sys.argv) == 2:
        root_dir = sys.argv[1]
    else:
        root_dir = os.getcwd()

    main(root_dir)
