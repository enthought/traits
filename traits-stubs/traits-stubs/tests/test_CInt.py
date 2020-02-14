from unittest import TestCase

from util import MypyAssertions


def code_block():
    from traits.api import HasTraits, BaseCInt

    class Test(HasTraits):
        i = BaseCInt()

    o = Test()
    o.i = "5"  # {ERR}
    o.i = 5
    o.i = 5.5  # {ERR}


def code_block2():
    from traits.api import HasTraits, BaseCInt

    class Test(HasTraits):
        i = BaseCInt(default_value="234")  # {ERR}

    class Test2(HasTraits):
        i = BaseCInt(default_value=234)


class TestInt(TestCase, MypyAssertions):

    def test_valid_values(self):
        self.assertRaisesMypyError(code_block)

    def test_invalid_default(self):
        self.assertRaisesMypyError(code_block2)
