import pickle
import unittest

from traits.api import Dict, HasTraits, Int, List


class C(HasTraits):
    # A dict trait containing a list trait
    a = Dict(Int, List(Int))

    # And we must initialize it to something non-trivial
    def __init__(self):
        super(C, self).__init__()
        self.a = {1: [2, 3]}


class PickleValidatedDictTestCase(unittest.TestCase):
    def test_pickle_validated_dict(self):

        # And we must unpickle one
        x = pickle.dumps(C())
        try:
            pickle.loads(x)
        except AttributeError as e:
            self.fail("Unpickling raised an AttributeError: %s" % e)
