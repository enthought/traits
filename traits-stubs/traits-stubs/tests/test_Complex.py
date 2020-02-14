from unittest import TestCase

from util import MypyAssertions


def code_block():
    from traits.api import Complex, HasTraits

    class Test(HasTraits):
        var = Complex()

    obj = Test()
    obj.var = "5"  # {ERR}
    obj.var = 5
    obj.var = 5.5
    obj.var = 5 + 4j


def code_block2():
    from traits.api import Complex, HasTraits

    class Test(HasTraits):
        var = Complex(default_value="sdf")  # {ERR}


class TestComplex(TestCase, MypyAssertions):

    def test_valid_values(self):
        self.assertRaisesMypyError(code_block)

    def test_invalid_default(self):
        self.assertRaisesMypyError(code_block2)
