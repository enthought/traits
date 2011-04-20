import unittest
from enthought.testing.api import doctest_for_module
import enthought.util.tree as tree

class TreeDocTestCase(doctest_for_module(tree)):
    pass

if __name__ == '__main__':
    import sys
    unittest.main(argv=sys.argv)
