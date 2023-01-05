# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.observation._generated_parser import (
    UnexpectedInput,
    Lark_StandAlone,
)

PARSER = Lark_StandAlone()


class TestParsingValidation(unittest.TestCase):
    """ Test parsing text using the standalone parser, for valid and invalid
    text, without further evaluation on the meaning of their content.
    """

    def test_invalid_examples(self):
        bad_examples = [
            "",
            "1name",
            "a.b.c^abc",
            "[a.b]c",
            "a*.c",
            "a:[b,c]:",
            ".a",
            "a()",
            "-a",
        ]
        for bad_example in bad_examples:
            with self.subTest(bad_example=bad_example):
                with self.assertRaises(UnexpectedInput):
                    PARSER.parse(bad_example)

    def test_valid_examples(self):
        good_examples = [
            "name",
            "name123",
            "name_a",
            "_name",
            "foo.bar",
            "foo  .  bar",
            "foo:bar",
            "foo  :  bar",
            "foo,bar",
            "foo  ,  bar",
            "[foo,bar,foo.spam]",
            "[foo, bar].baz",
            "[foo, [bar, baz]]:spam",
            "foo:[bar.spam,baz]",
            "foo.items",
            "items",
            "+metadata_name",
        ]

        for good_example in good_examples:
            with self.subTest(good_example=good_example):
                try:
                    PARSER.parse(good_example)
                except Exception:
                    self.fail(
                        "Parsing {!r} is expected to succeed.".format(
                            good_example
                        )
                    )
