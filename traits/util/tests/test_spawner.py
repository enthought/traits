#------------------------------------------------------------------------------
# Copyright (c) 2008, Enthought, Inc.
# All rights reserved.

import sys
import subprocess
import unittest
from os.path import dirname, join


class Tests(unittest.TestCase):

    def test_refresh(self):
        """
        run 'refresh.py' as a spawned process and test return value
        """
        path = join(dirname(__file__), 'refresh.py')
        subprocess.check_call([sys.executable, path])


if __name__ == "__main__":
    unittest.main()
