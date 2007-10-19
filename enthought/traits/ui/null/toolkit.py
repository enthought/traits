#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: David C. Morrill
# Date: 02/14/2005
#
#  Symbols defined: GUIToolkit
#
#------------------------------------------------------------------------------
""" Defines the concrete implementations of the traits Toolkit interface for
the 'null' (do nothing) user interface toolkit.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.ui.toolkit        import Toolkit
from enthought.traits.ui.editor_factory import EditorFactory

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Create a dummy singleton editor factory:
null_editor_factory = EditorFactory()

#-------------------------------------------------------------------------------
#  'GUIToolkit' class:
#-------------------------------------------------------------------------------

class GUIToolkit ( Toolkit ):

    #---------------------------------------------------------------------------
    #  GUI toolkit dependent trait definitions:
    #---------------------------------------------------------------------------

    def color_trait ( self, *args, **traits ):
        import color_trait as ct
        return ct.NullColor( *args, **traits )

    def rgb_color_trait ( self, *args, **traits ):
        import rgb_color_trait as rgbct
        return rgbct.RGBColor( *args, **traits )

    def font_trait ( self, *args, **traits ):
        import font_trait as ft
        return ft.NullFont( *args, **traits )

    def kiva_font_trait ( self, *args, **traits ):
        import font_trait as ft
        return ft.NullFont( *args, **traits )

    #---------------------------------------------------------------------------
    #  'EditorFactory' factory methods:
    #---------------------------------------------------------------------------

    def array_editor ( self, *args, **traits ):
        return null_editor_factory

    def boolean_editor ( self, *args, **traits ):
        return null_editor_factory

    def button_editor ( self, *args, **traits ):
        return null_editor_factory

    def check_list_editor ( self, *args, **traits ):
        return null_editor_factory

    def code_editor ( self, *args, **traits ):
        return null_editor_factory

    def color_editor ( self, *args, **traits ):
        return null_editor_factory

    def compound_editor ( self, *args, **traits ):
        return null_editor_factory

    def custom_editor ( self, *args, **traits ):
        return null_editor_factory

    def directory_editor ( self, *args, **traits ):
        return null_editor_factory

    def drop_editor ( self, *args, **traits ):
        return null_editor_factory

    def dnd_editor ( self, *args, **traits ):
        return null_editor_factory

    def enum_editor ( self, *args, **traits ):
        return null_editor_factory

    def file_editor ( self, *args, **traits ):
        return null_editor_factory

    def font_editor ( self, *args, **traits ):
        return null_editor_factory

    def key_binding_editor ( self, *args, **traits ):
        return null_editor_factory

    def html_editor ( self, *args, **traits ):
        return null_editor_factory

    def image_enum_editor ( self, *args, **traits ):
        return null_editor_factory

    def instance_editor ( self, *args, **traits ):
        return null_editor_factory

    def list_editor ( self, *args, **traits ):
        return null_editor_factory

    def null_editor ( self, *args, **traits ):
        return null_editor_factory

    def ordered_set_editor ( self, *args, **traits ):
        return null_editor_factory

    def plot_editor ( self, *args, **traits ):
        return null_editor_factory

    def range_editor ( self, *args, **traits ):
        return null_editor_factory

    def rgb_color_editor ( self, *args, **traits ):
        return null_editor_factory

    def rgba_color_editor ( self, *args, **traits ):
        return null_editor_factory

    def shell_editor ( self, *args, **traits ):
        return null_editor_factory

    def table_editor ( self, *args, **traits ):
        return null_editor_factory

    def text_editor ( self, *args, **traits ):
        return null_editor_factory

    def title_editor ( self, *args, **traits ):
        return null_editor_factory

    def tree_editor ( self, *args, **traits ):
        return null_editor_factory

    def tuple_editor ( self, *args, **traits ):
        return null_editor_factory

    def value_editor ( self, *args, **traits ):
        return null_editor_factory

