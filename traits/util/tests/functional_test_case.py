import sys, unittest
from enthought.testing.api import doctest_for_module
import enthought.util.functional as functional

class FunctionalDocTestCase(doctest_for_module(functional)):
    pass

if __name__ == '__main__':
    unittest.main(argv=sys.argv)
