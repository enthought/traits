from cPickle import dumps, loads
import unittest

from enthought.traits.api import Dict, HasTraits, Int, List

class C(HasTraits):

    # A dict trait containing a list trait
    a = Dict(Int, List(Int))

    # And we must initialize it to something non-trivial
    def __init__(self):
        super(C, self).__init__()
        self.a = {1 : [2,3]}

class PickleValidatedDictTestCase(unittest.TestCase):
    def test(self):

        # And we must unpickle one
        x = dumps(C())
        try:
            loads(x)
        except AttributeError, e:
            self.fail('Unpickling raised an AttributeError: %s' % e)

