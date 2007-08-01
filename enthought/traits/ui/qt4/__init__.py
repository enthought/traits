#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the concrete implementations of the traits Toolkit interface for 
the PyQt user interface toolkit.
"""
__import__('pkg_resources').declare_namespace(__name__)

#-------------------------------------------------------------------------------
#  Define the reference to the exported GUIToolkit object:
#-------------------------------------------------------------------------------
    
import toolkit

# Reference to the GUIToolkit object for PyQt.
toolkit = toolkit.GUIToolkit()
