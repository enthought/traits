# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Unittest tests on ListenerParser, ListenerBase etc.
See test_listeners for integration tests on the public API using these objects.

"""
from functools import partial
import unittest

from traits import traits_listener
from traits.api import (
    pop_exception_handler,
    push_exception_handler,
    TraitError,
    Undefined,
)


def assert_listener_item_equal(test_case, item1, item2, msg=None):
    """ Assertion function for comparing two instances of ListenerItem.
    """

    def get_msg(name, msg):
        return "{name} mismatched. {msg}".format(
            name=name,
            msg="" if msg is None else msg
        )

    test_case.assertEqual(
        item1.name, item2.name,
        msg=get_msg("name", msg),
    )
    test_case.assertEqual(
        item1.metadata_name, item2.metadata_name,
        msg=get_msg("metadata_name", msg),
    )
    test_case.assertEqual(
        item1.metadata_defined, item2.metadata_defined,
        msg=get_msg("metadata_defined", msg),
    )
    test_case.assertEqual(
        item1.is_anytrait, item2.is_anytrait,
        msg=get_msg("is_anytrait", msg),
    )
    test_case.assertEqual(
        item1.dispatch, item2.dispatch,
        msg=get_msg("dispatch", msg),
    )
    test_case.assertEqual(
        item1.notify, item2.notify,
        msg=get_msg("notify", msg),
    )
    test_case.assertEqual(
        item1.is_list_handler, item2.is_list_handler,
        msg=get_msg("is_list_handler", msg),
    )
    test_case.assertEqual(
        item1.type, item2.type,
        msg=get_msg("type", msg),
    )
    if item1.next is item2.next:
        # avoid recursion
        pass
    else:
        test_case.assertEqual(
            item1.next, item2.next,
            msg=get_msg("next", msg),
        )


class TestListenerParser(unittest.TestCase):

    def setUp(self):
        push_exception_handler(
            handler=lambda *args: None, reraise_exceptions=True)
        self.addTypeEqualityFunc(
            traits_listener.ListenerItem,
            partial(assert_listener_item_equal, self)
        )

    def tearDown(self):
        pop_exception_handler()

    def test_listener_parser_single_string(self):
        text = "some_trait_name"
        parser = traits_listener.ListenerParser(text=text)

        expected = traits_listener.ListenerItem(
            name="some_trait_name",
            metadata_name="",
            metadata_defined=True,
            is_anytrait=False,
            dispatch="",
            notify=True,
            is_list_handler=False,
            type=traits_listener.ANY_LISTENER,
            next=None,
        )
        self.assertEqual(parser.listener, expected)

    def test_listener_parser_trait_of_trait_dot(self):
        text = "parent.child"
        parser = traits_listener.ListenerParser(text=text)

        # then
        common_traits = dict(
            metadata_name="",
            metadata_defined=True,
            is_anytrait=False,
            dispatch="",
            notify=True,
            is_list_handler=False,
            type=traits_listener.ANY_LISTENER,
        )
        expected_child = traits_listener.ListenerItem(
            name="child",
            next=None,
            **common_traits
        )
        expected_parent = traits_listener.ListenerItem(
            name="parent",
            next=expected_child,
            **common_traits
        )
        self.assertEqual(parser.listener, expected_parent)

    def test_listener_parser_trait_of_trait_of_trait_mixed(self):
        text = "parent.child1:child2"
        parser = traits_listener.ListenerParser(text=text)

        # then
        common_traits = dict(
            metadata_name="",
            metadata_defined=True,
            is_anytrait=False,
            dispatch="",
            is_list_handler=False,
            type=traits_listener.ANY_LISTENER,
        )
        expected_child2 = traits_listener.ListenerItem(
            name="child2",
            notify=True,
            next=None,
            **common_traits
        )
        expected_child1 = traits_listener.ListenerItem(
            name="child1",
            notify=False,     # ':' indicates no notifications
            next=expected_child2,
            **common_traits
        )
        expected_parent = traits_listener.ListenerItem(
            name="parent",
            notify=True,
            next=expected_child1,
            **common_traits
        )
        self.assertEqual(parser.listener, expected_parent)

    def test_parse_comma_separated_text(self):
        text = "child1, child2, child3"
        parser = traits_listener.ListenerParser(text=text)

        listener_group = parser.listener

        common_traits = dict(
            metadata_name="",
            metadata_defined=True,
            is_anytrait=False,
            dispatch="",
            notify=True,
            is_list_handler=False,
            type=traits_listener.ANY_LISTENER,
            next=None,
        )
        expected_items = [
            traits_listener.ListenerItem(
                name="child1",
                **common_traits,
            ),
            traits_listener.ListenerItem(
                name="child2",
                **common_traits,
            ),
            traits_listener.ListenerItem(
                name="child3",
                **common_traits,
            ),
        ]
        self.assertEqual(len(listener_group.items), len(expected_items))
        for actual, expected in zip(listener_group.items, expected_items):
            self.assertEqual(actual, expected)

    def test_parse_comma_separated_text_trailing_comma(self):
        # Made illegal, see enthought/traits#406
        text = "child1, child2, child3,"
        with self.assertRaises(TraitError):
            traits_listener.ListenerParser(text=text)

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

        actual = parser.listener
        expected = traits_listener.ListenerItem(
            name="prefix",
            metadata_name="",
            metadata_defined=True,
            is_anytrait=False,
            dispatch="",
            notify=True,
            is_list_handler=False,
            type=traits_listener.ANY_LISTENER,
            # next is the ListenItem itself (so it is recursive)
            next=actual,
        )
        self.assertEqual(actual, expected)

    def test_parse_text_with_metadata(self):
        text = "prefix+foo"
        parser = traits_listener.ListenerParser(text=text)

        expected = traits_listener.ListenerItem(
            name="prefix*",
            metadata_name="foo",
            metadata_defined=True,
            is_anytrait=False,
            dispatch="",
            notify=True,
            is_list_handler=False,
            type=traits_listener.ANY_LISTENER,
            next=None,
        )
        self.assertEqual(parser.listener, expected)

    def test_parse_is_anytrait_plus(self):
        text = "+"
        parser = traits_listener.ListenerParser(text=text)

        expected = traits_listener.ListenerItem(
            name="*",
            metadata_name="",
            metadata_defined=True,
            is_anytrait=False,
            dispatch="",
            notify=True,
            is_list_handler=False,
            type=traits_listener.ANY_LISTENER,
            next=None,
        )
        self.assertEqual(parser.listener, expected)

    def test_parse_is_anytrait_minus(self):
        text = "-"
        parser = traits_listener.ListenerParser(text=text)

        expected = traits_listener.ListenerItem(
            name="*",
            metadata_name="",
            metadata_defined=False,    # the effect of '-'
            is_anytrait=True,         # the effect of '-'
            dispatch="",
            notify=True,
            is_list_handler=False,
            type=traits_listener.ANY_LISTENER,
            next=None,
        )
        self.assertEqual(parser.listener, expected)

    def test_parse_nested_exclude_empty_metadata_name(self):
        text = "foo-"
        parser = traits_listener.ListenerParser(text=text)

        expected = traits_listener.ListenerItem(
            name="foo*",
            metadata_name="",
            metadata_defined=False,    # the effect of '-'
            is_anytrait=False,
            dispatch="",
            notify=True,
            is_list_handler=False,
            type=traits_listener.ANY_LISTENER,
            next=None,
        )
        self.assertEqual(parser.listener, expected)

    def test_parse_exclude_metadata(self):
        text = "-foo"
        parser = traits_listener.ListenerParser(text=text)

        expected = traits_listener.ListenerItem(
            name="*",
            metadata_name="foo",
            metadata_defined=False,    # the effect of '-'
            is_anytrait=False,
            dispatch="",
            notify=True,
            is_list_handler=False,
            type=traits_listener.ANY_LISTENER,
            next=None,
        )
        self.assertEqual(parser.listener, expected)

    def test_parse_square_bracket(self):
        text = "[foo, bar]"
        parser = traits_listener.ListenerParser(text=text)
        listener_group = parser.listener

        # then
        common_traits = dict(
            metadata_name="",
            metadata_defined=True,
            is_anytrait=False,
            dispatch="",
            notify=True,
            is_list_handler=False,
            type=traits_listener.ANY_LISTENER,
            next=None,
        )
        expected_items = [
            traits_listener.ListenerItem(
                name="foo",
                **common_traits,
            ),
            traits_listener.ListenerItem(
                name="bar",
                **common_traits,
            )
        ]
        self.assertEqual(len(listener_group.items), len(expected_items))
        for actual, expected in zip(listener_group.items, expected_items):
            self.assertEqual(actual, expected)

    def test_parse_square_bracket_nested_attribute(self):
        text = "[foo, bar].baz"
        parser = traits_listener.ListenerParser(text=text)
        listener_group = parser.listener

        self.assertEqual(len(listener_group.items), 2)

        common_traits = dict(
            metadata_name="",
            metadata_defined=True,
            is_anytrait=False,
            dispatch="",
            notify=True,
            is_list_handler=False,
            type=traits_listener.ANY_LISTENER,
        )
        child_listener = traits_listener.ListenerItem(
            name="baz",
            next=None,
            **common_traits,
        )
        expected_items = [
            traits_listener.ListenerItem(
                name="foo",
                next=child_listener,
                **common_traits,
            ),
            traits_listener.ListenerItem(
                name="bar",
                next=child_listener,
                **common_traits,
            )
        ]
        self.assertEqual(len(listener_group.items), len(expected_items))
        for actual, expected in zip(listener_group.items, expected_items):
            self.assertEqual(actual, expected)

    def test_parse_square_bracket_in_middle(self):
        text = "foo.[bar, baz]"
        parser = traits_listener.ListenerParser(text=text)

        actual_foo = parser.listener
        # next is a ListenerGroup, and is checked separately
        actual_next = actual_foo.next
        actual_foo.next = None

        common_traits = dict(
            metadata_name="",
            metadata_defined=True,
            is_anytrait=False,
            dispatch="",
            notify=True,
            is_list_handler=False,
            type=traits_listener.ANY_LISTENER,
            next=None
        )
        expected_foo = traits_listener.ListenerItem(
            name="foo",
            **common_traits,
        )
        self.assertEqual(actual_foo, expected_foo)

        # Next listener is a ListenerGroup
        expected_items = [
            traits_listener.ListenerItem(
                name="bar",
                **common_traits,
            ),
            traits_listener.ListenerItem(
                name="baz",
                **common_traits,
            ),
        ]
        self.assertEqual(len(actual_next.items), len(expected_items))
        for actual, expected in zip(actual_next.items, expected_items):
            self.assertEqual(actual, expected)

    def test_parse_is_list_handler(self):
        text = "foo[]"
        parser = traits_listener.ListenerParser(text=text)

        expected = traits_listener.ListenerItem(
            name="foo",
            metadata_name="",
            metadata_defined=True,
            is_anytrait=False,
            dispatch="",
            notify=True,
            is_list_handler=True,    # the effect of '[]'
            type=traits_listener.ANY_LISTENER,
            next=None,
        )
        self.assertEqual(parser.listener, expected)

    def test_listener_handler_for_method(self):
        class A:
            def __init__(self, value):
                self.value = value

            def square(self):
                return self.value * self.value

        a = A(7)
        listener_handler = traits_listener.ListenerHandler(a.square)
        handler = listener_handler()
        self.assertEqual(handler(), 49)

        # listener_handler does not keep the object 'a' alive
        del a, handler
        handler = listener_handler()
        self.assertEqual(handler, Undefined)

    def test_listener_handler_for_function(self):

        def square(value):
            return value * value

        listener_handler = traits_listener.ListenerHandler(square)
        handler = listener_handler()
        self.assertEqual(handler(9), 81)

        # listener_handler *does* keep the 'square' function alive
        del square, handler
        handler = listener_handler()
        self.assertEqual(handler(5), 25)
