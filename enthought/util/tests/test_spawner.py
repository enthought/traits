#------------------------------------------------------------------------------
# Copyright (c) 2008, Enthought, Inc.
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# 
# Author: Ilan Schnell, Enthought, Inc.
#
# Description:
#     Unittest to run another (unittest) script directly.
#     In some cases this is necessary when things cannot be tested
#     with nosetests itself.
#------------------------------------------------------------------------------
import sys
import os.path
import subprocess
import unittest
from test.test_support import TESTFN

from enthought.util.resource import store_resource


class RefreshTestCase(unittest.TestCase):
    
    def test_refresh(self):
        """
            Run 'refresh.py' as a spawned process and test return value,
            The python source is stored into a temporary test file before
            being executed in a subprocess.
        """
        store_resource('EnthoughtBase',
                       os.path.join('enthought', 'util','tests', 'refresh.py'),
                       TESTFN)
        
        retcode = subprocess.call([sys.executable, TESTFN])
        
        self.assertEqual(retcode, 0)


    def tearDown(self):
        os.unlink(TESTFN)  
        

if __name__ == "__main__":
    unittest.main()
