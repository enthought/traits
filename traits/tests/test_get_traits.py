#------------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#------------------------------------------------------------------------------

from __future__ import absolute_import

from traits.testing.unittest_tools import unittest

from ..api import HasTraits, Int, Str, Undefined, ReadOnly, Float


class Foo(HasTraits):
    num = Int
    bar = Str

class Bar(HasTraits):
    PubT1   = Str                     #Default is public visible
    PubT1   = Str( visible=False )    #Change to invisible
    PrivT1  = Str( private=True )     #New behavior sets private Traits invisible
    PrivT2  = Str( private=True, visible=True ) #Make private traits visible
    

class GetTraitTestCase(unittest.TestCase):
    
    @unittest.expectedFailure
    def test_trait_set_bad(self):
        b = Foo()
        b.num = 'first'                         #This shall obviously fail (old and new behavior)
        self.failUnlessEqual(b.num, 'first')
        return
    
    def test_trait_set_replaced(self):
        b = Foo()
        b.add_trait( "num", Str() )             #Overriding the trait with a new type
        b.num = 'first'                         #Will work (not working before)
        self.failUnlessEqual(b.num, 'first')
        return
    
    def test_trait_set_replaced_and_check(self):
        b = Foo()
        b.add_trait( "num", Str() )
        b.num = 'first'
        #Ok for the first
        self.failUnlessEqual(b.num, 'first')
        
        #Should mean either way we ask for it we get the new one
        self.failUnlessEqual( b.trait("num"), b.traits()["num"] )    #Before the functions would return different traits!
        return
    
    
    def test_trait_names_returned_by_visible_traits(self):
        b = Bar()
        self.failUnlessEqual( b.visible_traits(), ["PubT1", "PrivT2"] )
        return


### EOF #######################################################################

if __name__ == '__main__':
    unittest.main()
