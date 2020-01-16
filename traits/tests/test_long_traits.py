import unittest

from traits.api import (
    BaseCInt,
    BaseCLong,
    BaseInt,
    BaseLong,
    CInt,
    CLong,
    Int,
    Long,
)


class TestLong(unittest.TestCase):
    def test_aliases(self):
        self.assertIs(BaseLong, BaseInt)
        self.assertIs(Long, Int)
        self.assertIs(BaseCLong, BaseCInt)
        self.assertIs(CLong, CInt)
