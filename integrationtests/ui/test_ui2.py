#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in /LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: David C. Morrill Date: 11/02/2004 Description: Test case for Traits
# User Interface
# ------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.kiva.traits.kiva_font_trait \
    import KivaFont

from enthought.enable.traits.api \
    import RGBAColor

from traits.api \
    import Trait, HasTraits, Str, Int, Range, List, Event, Bool

from traitsui.api \
    import View, Handler, Item, CheckListEditor, ButtonEditor, FileEditor, \
           DirectoryEditor, ImageEnumEditor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

origin_values = [ 'top left', 'top right', 'bottom left', 'bottom right' ]

#-------------------------------------------------------------------------------
#  'PersonHandler' class:
#-------------------------------------------------------------------------------

class PersonHandler ( Handler ):

    def object_zip_changed ( self, info ):
        obj     = info.object
        enabled = (obj.zip >= 10000)
        info.street.enabled = enabled
        info.city.enabled   = enabled
        info.state.enabled  = enabled
        if obj.zip == 78664:
            obj.street = '901 Morning View Place'
            obj.city   = 'Round Rock'
            obj.state  = 'Texas'

    def object_call_changed ( self, info ):
        print 'You called?'

#-------------------------------------------------------------------------------
#  'WizardHandler' class:
#-------------------------------------------------------------------------------

class WizardHandler ( Handler ):

    def object_sex_changed ( self, info ):
        if info.object.sex == 'Female':
            info.p1.next = 'p3'
        else:
            info.p1.next = 'p2'
            info.p2.next = None

    def object_name_changed ( self, info ):
        info.p2.enabled = info.p3.enabled = (info.object.name != '')
        if not info.p2.enabled:
            info.p2.msg = info.p3.msg = 'You must enter a valid name.'

#-------------------------------------------------------------------------------
#  'Employer' class:
#-------------------------------------------------------------------------------

class Employer ( HasTraits ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    company = Str
    boss    = Str

    view    = View( 'company', 'boss' )

#-------------------------------------------------------------------------------
#  'Person' class
#-------------------------------------------------------------------------------

class Person ( HasTraits ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    name      = Str( 'David Morrill' )
    age       = Int( 39 )
    sex       = Trait( 'Male', 'Female' )
    coolness  = Range( 0.0, 10.0, 10.0 )
    number    = Trait( 1, Range( 1, 6 ),
                       'one', 'two', 'three', 'four', 'five', 'six' )
    human     = Bool( True )
    employer  = Trait( Employer( company = 'Enthought, Inc.', boss = 'eric' ) )
    eye_color = RGBAColor
    set       = List( editor = CheckListEditor(
                                  values = [ 'one', 'two', 'three', 'four' ],
                                  cols   = 4 ) )
    font      = KivaFont
    street    = Str
    city      = Str
    state     = Str
    zip       = Int( 78663 )
    password  = Str
    books     = List( Str, [ 'East of Eden', 'The Grapes of Wrath',
                             'Of Mice and Men' ] )
    call      = Event( 0, editor = ButtonEditor( label = 'Click to call' ) )
    info      = Str( editor = FileEditor() )
    location  = Str( editor = DirectoryEditor() )
    origin    = Trait( editor = ImageEnumEditor( values = origin_values,
                                                 suffix = '_origin',
                                                 cols   = 4,
                                                 klass  = Employer ),
                       *origin_values )

    nm   = Item( 'name',     enabled_when = 'object.age >= 21' )
    pw   = Item( 'password', defined_when = 'object.zip == 78664' )
    view = View( ( ( nm, 'age', 'coolness',
                     '_', 'eye_color', 'eye_color@', 'eye_color*', 'eye_color~',
                     '_', 'font', 'font@', 'font*', 'font~',
                     '_', 'set', 'set@', 'set*', 'set~',
                     '_', 'sex', 'sex@', 'sex*', 'sex~',
                     '_', 'human', 'human@', 'human*', 'human~',
                     '_', 'number', 'number@', 'number*', 'number~',
                     '_', 'books', '_', 'books@', '_', 'books*', '_', 'books~',
                     '_', 'info', 'location', 'origin', 'origin@', 'call',
                     'employer', 'employer[]@', 'employer*', 'employer~',
                     pw,
                     '|<[Person:]' ),
                   ( ' ', 'street', 'city', 'state', 'zip', '|<[Address:]' ),
                   ( nm, nm, nm, nm, nm, nm, nm, nm, nm, nm, nm, nm, nm, nm,
                     '|<[Names:]' ),
                   '|' ),
                 title   = 'Traits 2 User Interface Test',
                 handler = PersonHandler(),
                 buttons = [ 'Apply', 'Revert', 'Undo', 'OK' ],
                 height  = 0.5 )

    wizard = View( ( '|p1:', 'name', 'age', 'sex' ),
                   ( '|p2:', 'street', 'city', 'state', 'zip' ),
                   ( '|p3:', 'eye_color', 'origin', 'human' ),
                   handler = WizardHandler() )

#-------------------------------------------------------------------------------
#  'TraitSheetApp' class:
#-------------------------------------------------------------------------------

class TraitSheetApp ( wx.App ):

    #---------------------------------------------------------------------------
    #  Initialize the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, object ):
        self.object = object
        wx.InitAllImageHandlers()
        wx.App.__init__( self, 1, 'debug.log' )
        self.MainLoop()
        object.print_traits()

    #---------------------------------------------------------------------------
    #  Handle application initialization:
    #---------------------------------------------------------------------------

    def OnInit ( self ):
        #ui = self.object.edit_traits( 'view', kind = 'live' )
        ui = self.object.edit_traits( 'wizard', kind = 'wizard' )
        self.SetTopWindow( ui.control )
        return True

#-------------------------------------------------------------------------------
#  Main program:
#-------------------------------------------------------------------------------

TraitSheetApp( Person() )

