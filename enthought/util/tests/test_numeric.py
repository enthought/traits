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
# Author: Enthought, Inc.
# Description: <Enthought util package component>
#------------------------------------------------------------------------------
from scipy import *

from enthought.util.numeric import *
import unittest
#from scipy_test.testing import assert_almost_equal, assert_array_almost_equal


class test_numeric(unittest.TestCase):
    
    def check_safe_take(self):
        a = array((1,2,3,4,2,2,7))
        b = array((2,2,2))
        indices = array((1,4,5))
        x = safe_take(a,indices)
        self.assert_(x == b)
    
        a = 2
        indices = array((0))
        x = safe_take(a,indices)
        self.assert_(x == a)
    
    def check_safe_copy(self):
        a = arange(1,4,1)
        x = safe_copy(a)
        self.assert_(x == a)
    
        a = 4.1
        x = safe_copy(a)
        self.assert_(x == a)
    
    def check_safe_min(self):
        a = array((1,2,3,4,5,-6,-7))
        x = safe_min(a)
        self.assert_(x == -7)
        
        a = 5.
        x = safe_min(a)
        self.assert_(x == 5.)
    
    def check_safe_max(self):
        a = array((1,2,3,4,5,-6,-7))
        x = safe_max(a)
        self.assert_(x == 5)
        
        a = 5.
        x = safe_max(a)
        self.assert_(x == 5.)
    
    def check_safe_len(self):
        a = array((1,2,3,4,5,-6,-7))
        x = safe_len(a)
        self.assert_(x == 7)
        
        a = 5.
        x = safe_len(a)
        self.assert_(x == 1)
            
    
def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append( unittest.makeSuite(test_math,'check_') )
    if level > 5:
        pass
    total_suite = unittest.TestSuite(suites)
    return total_suite

def test(level=10,verbosity=1):
    all_tests = test_suite(level=level)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(all_tests)
    return runner

if __name__ == "__main__":
    test()       
    
    