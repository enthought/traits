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
# Author: Enthought, Inc.
# Description: <Enthought util package component>
#------------------------------------------------------------------------------
import os.path
import subprocess
import unittest

# NOTE:
# `refresh_run.py` can not be run by nosetests directly because of
# the function refresh() in enthought.util.refresh.
# Therefore the test in this file (which nosetests will execute) will
# spawn a python interpreter running `refresh_run.py`.
# This test checks the return code of the process and will fail if
# the return code is non-zero.

class RefreshTestCase(unittest.TestCase):
    
    def test_run(self):
        """ Run `refresh_run.py` as a spawned process and test return value
        """
        retcode = subprocess.call(['python', 'refresh_run.py'],
                                  cwd=os.path.dirname(__file__))
        self.assert_(retcode == 0)
        

if __name__ == "__main__":          
    unittest.main()
