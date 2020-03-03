# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Unittest tests on ListenerParser, ListenBase etc.
See test_listeners for integration tests on the public API using these objects.

"""

import unittest

from traits import traits_listener
from traits.api import (
    TraitError,
    pop_exception_handler,
    push_exception_handler,
)


class TestListenerParser(unittest.TestCase):

    def setUp(self):
        push_exception_handler(
            handler=lambda *args: None, reraise_exceptions=True)

    def tearDown(self):
        pop_exception_handler()

    def test_listener_parser_single_string(self):
        text = "some_trait_name"
        parser = traits_listener.ListenerParser(text=text)

        listener = parser.listener
        self.assertEqual(listener.name, "some_trait_name")
        self.assertEqual(listener.metadata_name, "")
        self.assertTrue(listener.metadata_defined)
        self.assertFalse(listener.is_any_trait)
        self.assertEqual(listener.dispatch, "")
        self.assertTrue(listener.notify)
        self.assertFalse(listener.is_list_handler)
        self.assertEqual(listener.type, traits_listener.ANY_LISTENER)
        self.assertIsNone(listener.next)

    def test_listener_parser_trait_of_trait_dot(self):
        text = "parent.child"
        parser = traits_listener.ListenerParser(text=text)

        # parent listener
        listener = parser.listener
        self.assertEqual(listener.name, "parent")
        self.assertEqual(listener.metadata_name, "")
        self.assertTrue(listener.metadata_defined)
        self.assertFalse(listener.is_any_trait)
        self.assertEqual(listener.dispatch, "")
        self.assertTrue(listener.notify)
        self.assertFalse(listener.is_list_handler)
        self.assertEqual(listener.type, traits_listener.ANY_LISTENER)

        # child listener
        listener = listener.next
        self.assertEqual(listener.name, "child")
        self.assertEqual(listener.metadata_name, "")
        self.assertTrue(listener.metadata_defined)
        self.assertFalse(listener.is_any_trait)
        self.assertEqual(listener.dispatch, "")
        self.assertTrue(listener.notify)
        self.assertFalse(listener.is_list_handler)
        self.assertEqual(listener.type, traits_listener.ANY_LISTENER)
        self.assertIsNone(listener.next)

    def test_listener_parser_trait_of_trait_of_trait_mixed(self):
        text = "parent.child1:child2"
        parser = traits_listener.ListenerParser(text=text)

        # parent listener
        listener = parser.listener
        self.assertTrue(listener.notify, "'.' indicates notifications.")
        self.assertEqual(listener.name, "parent")
        self.assertEqual(listener.metadata_name, "")
        self.assertTrue(listener.metadata_defined)
        self.assertFalse(listener.is_any_trait)
        self.assertEqual(listener.dispatch, "")
        self.assertFalse(listener.is_list_handler)
        self.assertEqual(listener.type, traits_listener.ANY_LISTENER)

        # child1 listener
        listener = listener.next
        self.assertFalse(listener.notify, "':' indicates no notifications.")
        self.assertEqual(listener.name, "child1")
        self.assertEqual(listener.metadata_name, "")
        self.assertTrue(listener.metadata_defined)
        self.assertFalse(listener.is_any_trait)
        self.assertEqual(listener.dispatch, "")
        self.assertFalse(listener.is_list_handler)
        self.assertEqual(listener.type, traits_listener.ANY_LISTENER)

        # child2 listener
        listener = listener.next
        self.assertEqual(listener.name, "child2")
        self.assertEqual(listener.metadata_name, "")
        self.assertTrue(listener.metadata_defined)
        self.assertFalse(listener.is_any_trait)
        self.assertEqual(listener.dispatch, "")
        self.assertTrue(listener.notify)
        self.assertFalse(listener.is_list_handler)
        self.assertEqual(listener.type, traits_listener.ANY_LISTENER)
        self.assertIsNone(listener.next)

    def test_parse_comma_separated_text(self):
        text = "child1, child2, child3"
        parser = traits_listener.ListenerParser(text=text)

        listener_group = parser.listener

        self.assertEqual(len(listener_group.items), 3)

        for listener in listener_group.items:
            self.assertEqual(listener.metadata_name, "")
            self.assertTrue(listener.metadata_defined)
            self.assertFalse(listener.is_any_trait)
            self.assertEqual(listener.dispatch, "")
            self.assertTrue(listener.notify)
            self.assertFalse(listener.is_list_handler)
            self.assertEqual(listener.type, traits_listener.ANY_LISTENER)
            self.assertIsNone(listener.next)

        actual = [item.name for item in listener_group.items]
        self.assertEqual(actual, ["child1", "child2", "child3"])

    def test_parse_comma_separated_text_trailing_comma(self):
        text = "child1, child2, child3,"
        parser = traits_listener.ListenerParser(text=text)

        listener_group = parser.listener

        self.assertEqual(len(listener_group.items), 4)

        actual = [item.name for item in listener_group.items]
        self.assertEqual(actual, ["child1", "child2", "child3", ""])

    def test_parse_text_with_question_mark(self):
        text = "foo?.bar?"
        parser = traits_listener.ListenerParser(text=text)

        # parent
        listener = parser.listener
        self.assertEqual(listener.name, "foo?")

        # child
        listener = listener.next
        self.assertEqual(listener.name, "bar?")

    def test_parse_nested_empty_prefix_with_question_mark(self):
        text = "foo.?"
        with self.assertRaises(TraitError) as exception_context:
            traits_listener.ListenerParser(text=text)

        self.assertIn(
            "Expected non-empty name", str(exception_context.exception))

    def test_parse_question_mark_only(self):
        text = "?"
        with self.assertRaises(TraitError) as exception_context:
            traits_listener.ListenerParser(text=text)

        self.assertIn(
            "Expected non-empty name", str(exception_context.exception))

    def test_parse_with_asterisk(self):
        text = "prefix*"
        parser = traits_listener.ListenerParser(text=text)

        listener = parser.listener
        self.assertEqual(listener.name, "prefix")
        self.assertEqual(listener.metadata_name, "")
        self.assertTrue(listener.metadata_defined)
        self.assertFalse(listener.is_any_trait)
        self.assertEqual(listener.dispatch, "")
        self.assertTrue(listener.notify)
        self.assertFalse(listener.is_list_handler)
        self.assertEqual(listener.type, traits_listener.ANY_LISTENER)

        # next is itself (so it is recursive)
        self.assertIs(listener.next, listener)

    def test_parse_text_with_metadata(self):
        text = "prefix+foo"
        parser = traits_listener.ListenerParser(text=text)

        listener = parser.listener
        self.assertEqual(listener.name, "prefix*")
        self.assertEqual(listener.metadata_name, "foo")
        self.assertTrue(listener.metadata_defined)
        self.assertFalse(listener.is_any_trait)
        self.assertEqual(listener.dispatch, "")
        self.assertTrue(listener.notify)
        self.assertFalse(listener.is_list_handler)
        self.assertEqual(listener.type, traits_listener.ANY_LISTENER)
        self.assertIsNone(listener.next)

    def test_parse_is_any_trait_plus(self):
        text = "+"
        parser = traits_listener.ListenerParser(text=text)

        listener = parser.listener
        self.assertEqual(listener.name, "*")
        self.assertEqual(listener.metadata_name, "")
        self.assertTrue(listener.metadata_defined)
        self.assertFalse(listener.is_any_trait)
        self.assertEqual(listener.dispatch, "")
        self.assertTrue(listener.notify)
        self.assertFalse(listener.is_list_handler)
        self.assertEqual(listener.type, traits_listener.ANY_LISTENER)
        self.assertIsNone(listener.next)

    def test_parse_is_any_trait_minus(self):
        text = "-"
        parser = traits_listener.ListenerParser(text=text)

        listener = parser.listener
        self.assertEqual(listener.name, "*")
        self.assertEqual(listener.metadata_name, "")
        self.assertFalse(listener.metadata_defined)
        self.assertTrue(listener.is_any_trait)
        self.assertEqual(listener.dispatch, "")
        self.assertTrue(listener.notify)
        self.assertFalse(listener.is_list_handler)
        self.assertEqual(listener.type, traits_listener.ANY_LISTENER)
        self.assertIsNone(listener.next)

    def test_parse_nested_exclude_empty_metadata_name(self):
        text = "foo-"
        parser = traits_listener.ListenerParser(text=text)

        listener = parser.listener
        self.assertEqual(listener.name, "foo*")
        self.assertEqual(listener.metadata_name, "")
        self.assertFalse(listener.metadata_defined)
        self.assertFalse(listener.is_any_trait)
        self.assertEqual(listener.dispatch, "")
        self.assertTrue(listener.notify)
        self.assertFalse(listener.is_list_handler)
        self.assertEqual(listener.type, traits_listener.ANY_LISTENER)
        self.assertIsNone(listener.next)

    def test_parse_exclude_metadata(self):
        text = "-foo"
        parser = traits_listener.ListenerParser(text=text)

        listener = parser.listener
        self.assertEqual(listener.name, "*")
        self.assertEqual(listener.metadata_name, "foo")
        self.assertFalse(listener.metadata_defined)
        self.assertFalse(listener.is_any_trait)
        self.assertEqual(listener.dispatch, "")
        self.assertTrue(listener.notify)
        self.assertFalse(listener.is_list_handler)
        self.assertEqual(listener.type, traits_listener.ANY_LISTENER)
        self.assertIsNone(listener.next)

    def test_parse_square_bracket(self):
        text = "[foo, bar]"
        parser = traits_listener.ListenerParser(text=text)
        listener_group = parser.listener

        self.assertEqual(len(listener_group.items), 2)

        for listener in listener_group.items:
            self.assertEqual(listener.metadata_name, "")
            self.assertTrue(listener.metadata_defined)
            self.assertFalse(listener.is_any_trait)
            self.assertEqual(listener.dispatch, "")
            self.assertTrue(listener.notify)
            self.assertFalse(listener.is_list_handler)
            self.assertEqual(listener.type, traits_listener.ANY_LISTENER)
            self.assertIsNone(listener.next)

        actual = [item.name for item in listener_group.items]
        self.assertEqual(actual, ["foo", "bar"])

    def test_parse_square_bracket_nested_attribute(self):
        text = "[foo, bar].baz"
        parser = traits_listener.ListenerParser(text=text)
        listener_group = parser.listener

        self.assertEqual(len(listener_group.items), 2)

        for listener in listener_group.items:
            self.assertEqual(listener.metadata_name, "")
            self.assertTrue(listener.metadata_defined)
            self.assertFalse(listener.is_any_trait)
            self.assertEqual(listener.dispatch, "")
            self.assertTrue(listener.notify)
            self.assertFalse(listener.is_list_handler)
            self.assertEqual(listener.type, traits_listener.ANY_LISTENER)

            next_listener = listener.next
            self.assertEqual(next_listener.name, "baz")
            self.assertEqual(next_listener.metadata_name, "")
            self.assertTrue(next_listener.metadata_defined)
            self.assertFalse(next_listener.is_any_trait)
            self.assertEqual(next_listener.dispatch, "")
            self.assertTrue(next_listener.notify)
            self.assertFalse(next_listener.is_list_handler)
            self.assertEqual(next_listener.type, traits_listener.ANY_LISTENER)
            self.assertIsNone(next_listener.next)

        actual = [item.name for item in listener_group.items]
        self.assertEqual(actual, ["foo", "bar"])

    def test_parse_square_bracket_in_middle(self):
        text = "foo.[bar, baz]"
        parser = traits_listener.ListenerParser(text=text)
        listener = parser.listener

        self.assertEqual(listener.name, "foo")
        self.assertEqual(listener.metadata_name, "")
        self.assertTrue(listener.metadata_defined)
        self.assertFalse(listener.is_any_trait)
        self.assertEqual(listener.dispatch, "")
        self.assertTrue(listener.notify)
        self.assertFalse(listener.is_list_handler)
        self.assertEqual(listener.type, traits_listener.ANY_LISTENER)

        # Next listener is a ListenerGroup
        listener_group = listener.next
        self.assertEqual(len(listener_group.items), 2)
        actual = [item.name for item in listener_group.items]
        self.assertEqual(actual, ["bar", "baz"])

    def test_parse_is_list_handler(self):
        text = "foo[]"
        parser = traits_listener.ListenerParser(text=text)
        listener = parser.listener

        self.assertEqual(listener.name, "foo")
        self.assertEqual(listener.metadata_name, "")
        self.assertTrue(listener.metadata_defined)
        self.assertFalse(listener.is_any_trait)
        self.assertEqual(listener.dispatch, "")
        self.assertTrue(listener.notify)
        self.assertTrue(listener.is_list_handler)
        self.assertEqual(listener.type, traits_listener.ANY_LISTENER)
        self.assertIsNone(listener.next)
