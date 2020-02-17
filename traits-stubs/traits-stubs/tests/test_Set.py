from unittest import TestCase

from util import MypyAssertions


def code_block():
    from traits.api import HasTraits, Set, Int

    class Test(HasTraits):
        var = Set(trait=Int())

    obj = Test()
    obj.var = "5"  # {ERR}
    obj.var = 5  # {ERR}

    obj.var = False  # {ERR}
    obj.var = 5.5  # {ERR}

    obj.var = 5 + 4j  # {ERR}
    obj.var = True  # {ERR}

    obj.var = [1, 2, 3]
    obj.var = [1, 2, "3"]  # {ERR}


class TestSet(TestCase, MypyAssertions):

    def test_valid_values(self):
        self.assertRaisesMypyError(code_block)
