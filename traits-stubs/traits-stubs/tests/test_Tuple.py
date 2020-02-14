from unittest import TestCase

from util import MypyAssertions


def code_block():
    from traits.api import HasTraits, Tuple

    class Test(HasTraits):
        var = Tuple()

    obj = Test()
    obj.var = "5"  # {ERR}
    obj.var = 5  # {ERR}

    obj.var = False  # {ERR}
    obj.var = 5.5  # {ERR}

    obj.var = 5 + 4j  # {ERR}
    obj.var = True  # {ERR}

    obj.var = (True,)


class TestTuple(TestCase, MypyAssertions):

    def test_valid_values(self):
        self.assertRaisesMypyError(code_block)
