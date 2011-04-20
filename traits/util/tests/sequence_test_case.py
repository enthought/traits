import unittest
from enthought.testing.api import doctest_for_module
import enthought.util.sequence as sequence

class SequenceDocTestCase(doctest_for_module(sequence)):
    pass

if __name__ == '__main__':
    import sys
    unittest.main(argv=sys.argv)
