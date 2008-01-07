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

from enthought.util.math import *
import unittest
#from scipy_test.testing import assert_almost_equal, assert_array_almost_equal


class test_math(unittest.TestCase):
    
    def check_is_monotonic(self):
        a = array((1,2,3,4,5,6,7))
        self.assert_(is_monotonic(a) == True)
        a = array((1,2,3,-1000,5,6,7))
        self.assert_(is_monotonic(a) == False)
        a = array((1))
        self.assert_(is_monotonic(a) == False)
    
    def check_brange(self):
        a = brange(1,4,1)
        b = arange(1,5,1)
        self.assert_(a == b)
        
    
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
    
    