from unittest import TestCase

from util import MypyAssertions


def code_block():
    from traits.api import Bool, HasTraits

    class Test(HasTraits):
        var = Bool()

    obj = Test()
    obj.var = "5"  # {ERR}
    obj.var = 5  # {ERR}

    obj.var = False
    obj.var = 5.5  # {ERR}

    obj.var = 5 + 4j  # {ERR}
    obj.var = True


class TestBool(TestCase, MypyAssertions):

    def test_valid_values(self):
        self.assertRaisesMypyError(code_block)

