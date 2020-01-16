import unittest

from traits.api import (
    BaseCStr,
    BaseCUnicode,
    BaseStr,
    BaseUnicode,
    CStr,
    CUnicode,
    Str,
    Unicode,
)


class TestUnicodeTraits(unittest.TestCase):
    def test_aliases(self):
        self.assertIs(Unicode, Str)
        self.assertIs(CUnicode, CStr)
        self.assertIs(BaseUnicode, BaseStr)
        self.assertIs(BaseCUnicode, BaseCStr)
