from unittest import TestCase

from util import MypyAssertions


def code_block():
    from traits.api import HasTraits, Set, Int

    class Test(HasTraits):
        var = Set(trait=Int())

    obj = Test()
    obj.var = "5"
    obj.var = 5

    obj.var = False
    obj.var = 5.5

    obj.var = 5 + 4j
    obj.var = True

    obj.var = [1, 2, 3]
    obj.var = [1, 2, "3"]


class TestSet(TestCase, MypyAssertions):

    def test_valid_values(self):
        self.assertRaisesMypyError(code_block)
