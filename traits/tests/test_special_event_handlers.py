# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 13:58:00 2013

@author: yves
"""

from __future__ import division,print_function,unicode_literals,absolute_import

from traits.testing.unittest_tools import unittest

from ..api import HasStrictTraits, Str, Any

class TestSpecialEvent( unittest.TestCase ):
    """ Test demonstrating special change events using the 'event' metadata.
    """
    def setUp(self):
        self.change_events = []
        self.foo = Foo( test=self )
        return

    def test_events(self):
        self.foo.val = 'CHANGE'
        
        values = ['CHANGE']
        self.failUnlessEqual( self.change_events, values)
        return

    def test_instance_events(self):
        foo = self.foo
        foo.add_trait('val2',Str(event='the_trait'))
        foo.val2 = 'CHANGE2'
        
        values = ['CHANGE2']
        self.failUnlessEqual( self.change_events, values)
        return


class Foo(HasStrictTraits):
    val = Str(event='the_trait')
    test = Any(None)
    
    def _the_trait_changed(self,new):
        if self.test is not None:
            self.test.change_events.append(new)
    
    