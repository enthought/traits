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
    

class GetTraitTestCase(unittest.TestCase):
    
    @unittest.expectedFailure
    def test_trait_set_bad(self):
        b = Foo()
        b.num = 'first'
        self.failUnlessEqual(b.num, 'first')
        return
    
    def test_trait_set_replaced(self):
        b = Foo()
        b.add_trait( "num", Str() )
        b.num = 'first'
        self.failUnlessEqual(b.num, 'first')
        return
    
    def test_trait_set_replaced_and_check(self):
        b = Foo()
        b.add_trait( "num", Str() )
        b.num = 'first'
        #Ok for the first
        self.failUnlessEqual(b.num, 'first')
        
        #Should mean either way we ask for it we get the new one
        self.failUnlessEqual( b.trait("num"), b.traits()["num"] )
        
        return
    
    



### EOF #######################################################################

if __name__ == '__main__':
    unittest.main()
