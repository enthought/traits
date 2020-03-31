import contextlib
import unittest
from unittest import mock

import poc.observe as observe

from traits.api import HasTraits, Int, Instance, Str, List
from traits.constants import ComparisonMode
from traits.trait_base import Undefined

import logging


@contextlib.contextmanager
def set_logger():
    logger = logging.getLogger()
    level = logger.level
    handlers = list(logger.handlers)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger.handlers = [handler]
    logger.setLevel(logging.DEBUG)
    try:
        yield
    finally:
        logger.setLevel(level)
        logger.handlers = handlers


def log_all(f):
    def wrapped(*args, **kwargs):
        with set_logger():
            return f(*args, **kwargs)
    return wrapped


class TestList(unittest.TestCase):

    class Bar(HasTraits):

        age = Int()

    class Foo(HasTraits):

        l = List()

    def test_observer_is_quiet(self):
        # The callback is not called when we merely add an observer
        item_path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=False),
            observe.ListItemListener(notify=True),
        )
        f = self.Foo(l=[])
        mock_obj = mock.Mock()

        observe.observe(
            object=f,
            callback=mock_obj,
            path=item_path,
            remove=False,
            dispatch="same",
        )
        mock_obj.assert_not_called()

    def test_mutate_nested_attribute(self):
        age_path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=False),
            observe.ListItemListener(notify=False),
            observe.RequiredTraitListener(name="age", notify=True),
        )
        f = self.Foo(l=[self.Bar()])
        mock_obj = mock.Mock()

        observe.observe(
            object=f,
            callback=mock_obj,
            path=age_path,
            remove=False,
            dispatch="same",
        )

        f.l[0].age = 20

        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertEqual(event.old, 0)
        self.assertEqual(event.new, 20)

    def test_append_list(self):
        item_path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=False),
            observe.ListItemListener(notify=True),
        )
        f = self.Foo(l=[])
        mock_obj = mock.Mock()

        observe.observe(
            object=f,
            callback=mock_obj,
            path=item_path,
            remove=False,
            dispatch="same",
        )

        bar = self.Bar()
        f.l.append(bar)

        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertIs(event.new, f.l)
        self.assertEqual(event.index, 0)
        self.assertEqual(event.removed, [])
        self.assertEqual(event.added, [bar])

    def test_extend_list(self):
        item_path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=False),
            observe.ListItemListener(notify=True),
        )
        f = self.Foo(l=[])
        mock_obj = mock.Mock()

        observe.observe(
            object=f,
            callback=mock_obj,
            path=item_path,
            remove=False,
            dispatch="same",
        )

        bar = self.Bar()
        f.l.extend((bar, bar))

        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertIs(event.new, f.l)
        self.assertEqual(event.removed, [])
        self.assertEqual(event.added, [bar, bar])

    def test_list_setitem_many(self):

        path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=False),
            observe.ListItemListener(notify=True),
            # Need this listener so we exercise logic for
            # propagating listeners to extended attributes when
            # the list is mutated.
            observe.RequiredTraitListener(name="age", notify=True),
        )
        f = self.Foo(l=[self.Bar(), self.Bar(), self.Bar()])
        mock_obj = mock.Mock()

        observe.observe(
            object=f,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        # when
        new_bars = [self.Bar(), self.Bar()]
        old_bars = list(f.l[::2])
        f.l[::2] = new_bars

        # then
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertEqual(event.removed, old_bars)
        self.assertEqual(event.added, new_bars)

    def test_list_setitem_one(self):

        path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=False),
            observe.ListItemListener(notify=True),
            # Need this listener so we exercise logic for
            # propagating listeners to extended attributes when
            # the list is mutated.
            observe.RequiredTraitListener(name="age", notify=True),
        )
        f = self.Foo(l=[self.Bar(), self.Bar(), self.Bar()])
        mock_obj = mock.Mock()

        observe.observe(
            object=f,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        # when
        new_bar = self.Bar()
        old_bars = [f.l[0]]
        f.l[0] = new_bar

        # then
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertEqual(event.removed, old_bars)
        self.assertEqual(event.added, [new_bar])

    def test_list_delitem_one(self):

        path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=False),
            observe.ListItemListener(notify=True),
            # Need this listener so we exercise logic for
            # propagating listeners to extended attributes when
            # the list is mutated.
            observe.RequiredTraitListener(name="age", notify=True),
        )
        f = self.Foo(l=[self.Bar(), self.Bar(), self.Bar()])
        mock_obj = mock.Mock()

        observe.observe(
            object=f,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        old_bars = [f.l[0]]

        # when
        # Delete all items
        del f.l[0]

        # then
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertEqual(event.removed, old_bars)
        self.assertEqual(event.added, [])

    def test_list_delitem_many(self):

        path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=False),
            observe.ListItemListener(notify=True),
            # Need this listener so we exercise logic for
            # propagating listeners to extended attributes when
            # the list is mutated.
            observe.RequiredTraitListener(name="age", notify=True),
        )
        f = self.Foo(l=[self.Bar(), self.Bar(), self.Bar()])
        mock_obj = mock.Mock()

        observe.observe(
            object=f,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        old_bars = list(f.l)

        # when
        # Delete all items
        del f.l[:]

        # then
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertEqual(event.removed, old_bars)
        self.assertEqual(event.added, [])

    def test_list_insert(self):
        path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=False),
            observe.ListItemListener(notify=True),
            # Need this listener so we exercise logic for
            # propagating listeners to extended attributes when
            # the list is mutated.
            observe.RequiredTraitListener(name="age", notify=True),
        )
        f = self.Foo(l=[self.Bar(), self.Bar(), self.Bar()])
        mock_obj = mock.Mock()

        observe.observe(
            object=f,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        # when
        new_bar = self.Bar()
        f.l.insert(1, new_bar)

        # then
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertEqual(event.removed, [])
        self.assertEqual(event.added, [new_bar])

    def test_list_clear(self):
        path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=False),
            observe.ListItemListener(notify=True),
            # Need this listener so we exercise logic for
            # propagating listeners to extended attributes when
            # the list is mutated.
            observe.RequiredTraitListener(name="age", notify=True),
        )
        f = self.Foo(l=[self.Bar(), self.Bar(), self.Bar()])
        mock_obj = mock.Mock()

        observe.observe(
            object=f,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        old_bars = list(f.l)

        # when
        f.l.clear()

        # then
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertEqual(event.removed, old_bars)
        self.assertEqual(event.added, [])

    def test_list_pop(self):
        path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=False),
            observe.ListItemListener(notify=True),
            # Need this listener so we exercise logic for
            # propagating listeners to extended attributes when
            # the list is mutated.
            observe.RequiredTraitListener(name="age", notify=True),
        )
        f = self.Foo(l=[self.Bar(), self.Bar(), self.Bar()])
        mock_obj = mock.Mock()

        observe.observe(
            object=f,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        # when
        popped = f.l.pop()

        # then
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertEqual(event.removed, [popped])
        self.assertEqual(event.added, [])

    def test_list_remove(self):
        path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=False),
            observe.ListItemListener(notify=True),
            # Need this listener so we exercise logic for
            # propagating listeners to extended attributes when
            # the list is mutated.
            observe.RequiredTraitListener(name="age", notify=True),
        )
        f = self.Foo(l=[self.Bar(), self.Bar(), self.Bar()])
        mock_obj = mock.Mock()

        observe.observe(
            object=f,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        bar_to_be_removed = f.l[1]

        # when
        f.l.remove(bar_to_be_removed)

        # then
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertEqual(event.removed, [bar_to_be_removed])
        self.assertEqual(event.added, [])

    def test_mutate_object_added_later(self):
        # Test when a nested object is appened to the list after registering
        # the observer.
        age_path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=False),
            observe.ListItemListener(notify=False),
            observe.RequiredTraitListener(name="age", notify=True),
        )
        f = self.Foo(l=[])
        mock_obj = mock.Mock()

        observe.observe(
            object=f,
            callback=mock_obj,
            path=age_path,
            remove=False,
            dispatch="same",
        )

        # when
        bar = self.Bar()
        f.l.append(bar)

        # then
        # There are no notifiers for these changes
        mock_obj.assert_not_called()

        # when
        bar.age = 20

        # then
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertEqual(event.old, 0)
        self.assertEqual(event.new, 20)

    def test_mutate_removed_object(self):
        # Test when an object is removed from the list,
        # no change events are fired
        age_path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=False),
            observe.ListItemListener(notify=False),
            observe.RequiredTraitListener(name="age", notify=True),
        )
        bar = self.Bar()
        f = self.Foo(l=[])
        mock_obj = mock.Mock()
        observe.observe(
            object=f,
            callback=mock_obj,
            path=age_path,
            remove=False,
            dispatch="same",
        )

        # when
        f.l.append(bar)
        bar.age = 10

        # then
        self.assertEqual(mock_obj.call_count, 1)

        # when
        mock_obj.reset_mock()
        f.l.pop()
        bar.age = 11

        # then
        mock_obj.assert_not_called()

    def test_newly_assigned_list(self):
        age_path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=False),
            observe.ListItemListener(notify=False),
            observe.RequiredTraitListener(name="age", notify=True),
        )

        foo = self.Foo()
        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=age_path,
            remove=False,
            dispatch="same",
        )

        # when
        # New assignment after observe is called
        bar = self.Bar()
        foo.l = [bar]
        bar.age = 10

        # then
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertEqual(event.old, 0)
        self.assertEqual(event.new, 10)

    def test_newly_assigned_list_append(self):
        # Test appending to a new list assigned to a trait
        item_path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=False),
            observe.ListItemListener(notify=True),
        )

        foo = self.Foo()
        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=item_path,
            remove=False,
            dispatch="same",
        )

        foo.l = [1, 2]

        # when
        # assign to a new list that compares equal does not fire events
        mock_obj.reset_mock()
        foo.l = [1, 2]

        # then
        mock_obj.assert_not_called()

        # when
        foo.l.append(3)

        # then
        self.assertEqual(mock_obj.call_count, 1)

    def test_implicit_default_list(self):
        # Test when a list attribute is accessed the first time,
        # the default list created will also receive the notifiers.
        list_path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=True),
            observe.ListItemListener(notify=True),
        )

        foo = self.Foo()
        # The list is not defined explicitly. It is still undefined at
        # this point.
        self.assertNotIn("l", foo.__dict__)

        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=list_path,
            remove=False,
            dispatch="same",
        )

        # when
        foo.l   # implicitly created the list, which is the default

        # then
        mock_obj.assert_not_called()

        # when
        foo.l.append(3)

        # then
        self.assertEqual(mock_obj.call_count, 1)

    def test_resurrect_existing_behaviour_compare_equal(self):
        # We may not need to silence event when the new list
        # compares equally to the old list after all?
        # Let's see if we could!
        list_path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=True),
            observe.ListItemListener(notify=True),
        )

        foo = self.Foo(l=[1, 2, 3])

        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe.RequiredTraitListener(
                    name="l",
                    notify=True,
                    comparison_mode=ComparisonMode.equality,
                ),
                observe.ListItemListener(notify=True),
            ),
            remove=False,
            dispatch="same",
        )

        # when
        # Compares equally to the old list...
        foo.l = [1, 2, 3]

        # then
        mock_obj.assert_not_called()

        # when
        foo.l.append(4)

        # then
        # should still fire for mutation.
        self.assertEqual(mock_obj.call_count, 1)


class TestListOfList(unittest.TestCase):

    def test_nested_list_of_list_of_list(self):
        # notify changes on the most nested list, but not anything else.

        class Foo(HasTraits):

            bars = List(List(List()))

        path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="bars", notify=False),
            observe.ListItemListener(notify=False),
            observe.ListItemListener(notify=False),
            observe.ListItemListener(notify=True),
        )

        foo = Foo()
        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        # when
        foo.bars = [[[]]]

        # then
        mock_obj.assert_not_called()

        # when
        foo.bars[0][0].append(1)

        # then
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertEqual(event.added, [1])

    def test_nested_list_of_list_reassigned(self):

        class Foo(HasTraits):

            bars = List(List())

        path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="bars", notify=True),
            observe.ListItemListener(notify=True),
            observe.ListItemListener(notify=True),
        )

        foo = Foo()
        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        # when
        foo.bars = [[1, 2]]

        # then
        # for the new assignment of foo.bars
        # Note that the implicit default for foo.bars before assignment was `[]`
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertIs(event.object, foo)
        self.assertEqual(event.name, "bars")
        self.assertEqual(event.old, [])
        self.assertEqual(event.new, [[1, 2]])

        # when
        mock_obj.reset_mock()
        foo.bars[0].append(3)

        # then
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertIs(event.new, foo.bars[0])
        self.assertEqual(event.index, 2)
        self.assertEqual(foo.bars, [[1, 2, 3]])

        # when
        mock_obj.reset_mock()
        foo.bars = [[1, 2]]

        # then
        self.assertEqual(mock_obj.call_count, 1)

        # when
        mock_obj.reset_mock()
        foo.bars[0] = [3]

        # then
        self.assertEqual(mock_obj.call_count, 1)

        # when
        self.assertEqual(foo.bars, [[3]])
        mock_obj.reset_mock()
        foo.bars = [[3]]

        # then
        # TODO: This is a change from existing behaviour.
        # Old list does not fire event for this.
        self.assertEqual(mock_obj.call_count, 1)
        mock_obj.reset_mock()

        # when
        foo.bars[0] = [4]

        # then
        self.assertEqual(mock_obj.call_count, 1)

    def test_nested_list_of_list_of_list_reassigned(self):

        class Foo(HasTraits):

            bars = List(List(List()))

        path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="bars", notify=False),
            observe.ListItemListener(notify=False),
            observe.ListItemListener(notify=False),
            observe.ListItemListener(notify=True),
        )

        foo = Foo(bars=[[[]]])
        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        # when
        foo.bars[0][0].append(1)

        # then
        self.assertEqual(mock_obj.call_count, 1)

        # when
        # Reassign to a new list that compares equal.
        self.assertEqual(foo.bars[0], [[1]])
        foo.bars[slice(0, 1)] = [[[1]]]
        self.assertEqual(foo.bars[0], [[1]])

        mock_obj.reset_mock()
        foo.bars[0][0].append(2)

        # then
        self.assertEqual(mock_obj.call_count, 1)


class TestIssue538(unittest.TestCase):

    def test_issue_538(self):
        # It seems that the issue stamps from the implicit "_items"
        # when `children` is a list
        # Here, the listeners are made explicit.

        class Child(HasTraits):

            value = Int()

        class Parent(HasTraits):

            children = List(Instance(Child))

        path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="children", notify=False),
            observe.ListItemListener(notify=True),
            observe.RequiredTraitListener(name="value", notify=True),
        )

        parent = Parent()
        mock_obj = mock.Mock()
        observe.observe(
            object=parent,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        # when
        parent.children = [Child(value=1)]

        # then
        mock_obj.assert_not_called()

        # when
        mock_obj.reset_mock()
        second_child = Child(value=2)
        parent.children.append(second_child)

        # then
        self.assertEqual(mock_obj.call_count, 1)

        # when
        mock_obj.reset_mock()
        parent.children.append(second_child)

        # then
        self.assertEqual(mock_obj.call_count, 1)

        # when
        mock_obj.reset_mock()
        second_child.value += 1

        # then
        self.assertEqual(mock_obj.call_count, 1)


class TestIssue537(unittest.TestCase):

    def test_issue_537(self):

        class Child(HasTraits):

            values = List(Int)

        class Parent(HasTraits):

            child = Instance(Child)
            values = List(Int)

        parent = Parent(
            child=Child(values=[1, 2, 3]),
            values=[4, 5, 6],
        )

        mock_obj = mock.Mock()
        values_path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="values", notify=True),
        )
        observe.observe(
            object=parent,
            callback=mock_obj,
            path=values_path,
            remove=False,
            dispatch="same",
        )
        child_values_path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="child", notify=True),
            observe.RequiredTraitListener(name="values", notify=True),
        )
        observe.observe(
            object=parent,
            callback=mock_obj,
            path=child_values_path,
            remove=False,
            dispatch="same",
        )
        # when
        parent.values[0] = 100

        # then
        mock_obj.assert_not_called()

        # when
        parent.child.values[0] = 100

        # then
        mock_obj.assert_not_called()


class TestIssue237(unittest.TestCase):

    def test_multiple_identical_object_in_list(self):
        # enthought/traits#237

        class Bar(HasTraits):
            age = Int()

        class Foo(HasTraits):
            l = List(Instance(Bar))

        age_path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="l", notify=False),
            observe.ListItemListener(notify=False),
            observe.RequiredTraitListener(name="age", notify=True),
        )
        f = Foo(l=[])
        mock_obj = mock.Mock()

        observe.observe(
            object=f,
            callback=mock_obj,
            path=age_path,
            remove=False,
            dispatch="same",
        )

        bar = Bar()
        f.l.extend((bar, bar))
        mock_obj.assert_not_called()

        # when
        bar.age = 20

        # then
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertEqual(event.old, 0)
        self.assertEqual(event.new, 20)

        # when
        # pop one item, the same object is still in the list
        mock_obj.reset_mock()
        f.l.pop()
        bar.age = 21

        # then
        self.assertIn(bar, f.l)
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertEqual(event.old, 20)
        self.assertEqual(event.new, 21)

    def test_issue_237_list_of_list_of_instance(self):

        class Baz(HasTraits):

            value = Int()

        class Bar(HasTraits):

            bazs = List(Instance(Baz))

        class Foo(HasTraits):

            bars = List(Instance(Bar))

        baz = Baz(value=0)
        foo = Foo(
            bars=[
                Bar(bazs=[baz]),
                Bar(bazs=[baz]),
            ]
        )
        path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="bars", notify=False),
            observe.ListItemListener(notify=False),
            observe.RequiredTraitListener(name="bazs", notify=False),
            observe.ListItemListener(notify=False),
            observe.RequiredTraitListener(name="value", notify=True),
        )
        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        baz.value = 2
        self.assertEqual(mock_obj.call_count, 1)

        foo.bars[0].bazs.pop()

        mock_obj.reset_mock()
        baz.value = 3
        self.assertEqual(mock_obj.call_count, 1)

        foo.bars[1].bazs.pop()

        mock_obj.reset_mock()
        baz.value = 4
        mock_obj.assert_not_called()

    def test_issue_237_different_level_of_nesting(self):

        class Baz(HasTraits):

            value = Int()

        class Bar(HasTraits):

            bazs = List(Instance(Baz))

        class Spam(HasTraits):

            bars = List(Instance(Bar))

        class Foo(HasTraits):

            bars = List(Instance(Bar))

            spams = List(Instance(Spam))

        baz = Baz(value=1)
        foo = Foo(
            bars=[
                Bar(bazs=[baz]),
                Bar(bazs=[baz]),
            ],
            spams=[
                Spam(
                    bars=[
                        Bar(bazs=[baz]),
                        Bar(bazs=[baz]),
                    ]
                )
            ]
        )
        mock_obj = mock.Mock()
        # "bars:bazs:value"
        path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="bars", notify=False),
            observe.ListItemListener(notify=False),
            observe.RequiredTraitListener(name="bazs", notify=False),
            observe.ListItemListener(notify=False),
            observe.RequiredTraitListener(name="value", notify=True)
        )
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        # when
        mock_obj.reset_mock()
        baz.value += 1

        # then
        self.assertEqual(mock_obj.call_count, 1)

        # when
        # Add one more listener... which walks a different path!
        # "spams:bars:bazs:value"
        path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="spams", notify=False),
            observe.ListItemListener(notify=False),
            observe.RequiredTraitListener(name="bars", notify=False),
            observe.ListItemListener(notify=False),
            observe.RequiredTraitListener(name="bazs", notify=False),
            observe.ListItemListener(notify=False),
            observe.RequiredTraitListener(name="value", notify=True)
        )
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        # when
        mock_obj.reset_mock()
        baz.value += 1

        # then
        # It is the same callback
        self.assertEqual(mock_obj.call_count, 1)

    def test_issue_237_different_level_of_nesting_different_target(self):
        # Test when the observer is called different objects, the same
        # callback is attached more than once.

        class Baz(HasTraits):

            value = Int()

        class Bar(HasTraits):

            bazs = List(Instance(Baz))

        class Spam(HasTraits):

            bars = List(Instance(Bar))

        class Foo(HasTraits):

            bars = List(Instance(Bar))

            spams = List(Instance(Spam))

        baz = Baz(value=1)
        foo = Foo(
            bars=[
                Bar(bazs=[baz]),
                Bar(bazs=[baz]),
            ],
            spams=[
                Spam(
                    bars=[
                        Bar(bazs=[baz]),
                        Bar(bazs=[baz]),
                    ]
                )
            ]
        )

        spam = foo.spams[0]

        # Listen to change in `Spam`
        mock_obj = mock.Mock()
        observe.observe(
            object=spam,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe.RequiredTraitListener(name="bars", notify=False),
                observe.ListItemListener(notify=False),
                observe.RequiredTraitListener(name="bazs", notify=False),
                observe.ListItemListener(notify=False),
                observe.RequiredTraitListener(name="value", notify=True)
            ),
            remove=False,
            dispatch="same",
        )

        # Listen to change on `Foo`
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe.RequiredTraitListener(name="bars", notify=False),
                observe.ListItemListener(notify=False),
                observe.RequiredTraitListener(name="bazs", notify=False),
                observe.ListItemListener(notify=False),
                observe.RequiredTraitListener(name="value", notify=True)
            ),
            remove=False,
            dispatch="same",
        )

        # Modifying the shared baz will cause both notifiers to fire.
        baz.value += 1

        self.assertEqual(mock_obj.call_count, 2)


class TestFilteredTrait(unittest.TestCase):

    def test_filter_metadata(self):

        class Foo(HasTraits):

            age = Int(public=False)
            name = Str(public=True)
            gender = Str(public=True)

        path = observe.ListenerPath.from_nodes(
            observe._FilteredTraitListener(notify=True, filter=lambda _, trait: trait.public),
        )

        foo = Foo(age=1, name="John", gender="male")
        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        # when
        foo.age = 2

        # then
        mock_obj.assert_not_called()

        # when
        foo.name = "Jim"

        # then
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertIs(event.object, foo)
        self.assertEqual(event.name, "name")
        self.assertEqual(event.old, "John")
        self.assertEqual(event.new, "Jim")

        # when
        mock_obj.reset_mock()
        foo.gender = "unknown"

        # then
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertIs(event.object, foo)
        self.assertEqual(event.name, "gender")
        self.assertEqual(event.old, "male")
        self.assertEqual(event.new, "unknown")

    def test_filter_metadata_nested_attribute(self):

        class Person(HasTraits):
            name = Str(public=True)
            age = Int(public=False)

        class Foo(HasTraits):
            guardian = Instance(Person, public=True)
            mother = Instance(Person, public=False)

        path = observe.ListenerPath.from_nodes(
            observe._FilteredTraitListener(
                notify=False, filter=lambda _, trait: trait.public),
            observe._FilteredTraitListener(
                notify=True, filter=lambda _, trait: trait.public),
        )
        foo = Foo(
            guardian=Person(name="John", age=40),
            mother=Person(name="Mother", age=35),
        )
        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        # when
        foo.guardian.age = 41

        # then
        mock_obj.assert_not_called()

        # when
        foo.guardian.name = "Jim"

        # then
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertIs(event.object, foo.guardian)
        self.assertEqual(event.name, "name")
        self.assertEqual(event.old, "John")
        self.assertEqual(event.new, "Jim")

        # when
        mock_obj.reset_mock()
        foo.mother.age = 31

        # then
        mock_obj.assert_not_called()

        # when
        mock_obj.reset_mock()
        foo.mother.name = "Holly"

        # then
        mock_obj.assert_not_called()

    def test_filter_metadata_parent_changed(self):

        class Person(HasTraits):
            name = Str(public=True)
            age = Int(public=False)

        class Foo(HasTraits):
            guardian = Instance(Person, public=True)
            mother = Instance(Person, public=False)

        path = observe.ListenerPath.from_nodes(
            observe._FilteredTraitListener(
                notify=False, filter=lambda _, trait: trait.public),
            observe._FilteredTraitListener(
                notify=True, filter=lambda _, trait: trait.public),
        )
        foo = Foo(
            guardian=Person(name="John", age=40),
            mother=Person(name="Mother", age=35),
        )
        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        # when
        foo.guardian = Person(name="Jim", age=41)

        # then
        # notify is False
        mock_obj.assert_not_called()

        # when
        foo.guardian.name = "Terry"

        # then
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertIs(event.object, foo.guardian)
        self.assertEqual(event.name, "name")
        self.assertEqual(event.old, "Jim")
        self.assertEqual(event.new, "Terry")

        # when
        mock_obj.reset_mock()
        foo.mother = Person(name="Mary", age=50)

        # then
        mock_obj.assert_not_called()

        # when
        foo.mother.name = "Wendy"

        # then
        # mother is not public info
        mock_obj.assert_not_called()

    def test_filter_metadata_parent_uninitialized(self):

        class Person(HasTraits):
            name = Str(public=True)
            age = Int(public=False)

        class Foo(HasTraits):
            guardian = Instance(Person, public=True)
            mother = Instance(Person, public=False)

        path = observe.ListenerPath.from_nodes(
            observe._FilteredTraitListener(
                notify=False, filter=lambda _, trait: trait.public),
            observe._FilteredTraitListener(
                notify=True, filter=lambda _, trait: trait.public),
        )

        # The instances are not initialized, and will have a value None.
        foo = Foo()
        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        # when
        foo.guardian = Person(name="Jim", age=41)

        # then
        # notify is False
        mock_obj.assert_not_called()

        # when
        foo.guardian.name = "Terry"

        # then
        self.assertEqual(mock_obj.call_count, 1)


class TestRemoveNotifier(unittest.TestCase):

    def test_notifer_removed_for_removed_object(self):

        class Baz(HasTraits):
            value = Int()

        class Bar(HasTraits):
            baz = Instance(Baz)

        class Foo(HasTraits):
            bar = Instance(Bar)

        path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="bar", notify=False),
            observe.RequiredTraitListener(name="baz", notify=False),
            observe.RequiredTraitListener(name="value", notify=True),
        )
        foo = Foo(bar=Bar(baz=Baz(value=10)))

        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        # when
        bar = foo.bar
        foo.bar = Bar(baz=Baz(value=11))

        # then
        mock_obj.assert_not_called()

        # when
        bar.baz.value += 1

        # then
        mock_obj.assert_not_called()

    def test_remove_notifier_manually(self):

        class Bar(HasTraits):
            value = Int()

        class Foo(HasTraits):
            bar = Instance(Bar)

        path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="bar", notify=True),
            observe.RequiredTraitListener(name="value", notify=True),
        )
        foo = Foo(bar=Bar())

        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=path,
            remove=False,
            dispatch="same",
        )

        # verify the notifiers are set...
        foo.bar = Bar()
        self.assertEqual(mock_obj.call_count, 1)
        mock_obj.reset_mock()
        foo.bar.value += 1
        self.assertEqual(mock_obj.call_count, 1)

        # when
        # define a new path, make sure we don't depend on
        # the same ListenerPath object.
        path = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="bar", notify=True),
            observe.RequiredTraitListener(name="value", notify=True),
        )
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=path,
            remove=True,
            dispatch="same",
        )

        # then
        mock_obj.reset_mock()
        foo.bar.value += 1
        mock_obj.assert_not_called()

        mock_obj.reset_mock()
        foo.bar = Bar()
        mock_obj.assert_not_called()

    def test_remove_path_with_metadata_filter(self):
        # test cleaning up paths involving metadata file.

        class Bar(HasTraits):

            age = Int(public=True)

        class Foo(HasTraits):

            bar = Instance(Bar())

        foo = Foo(bar=Bar())

        # add two paths
        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe.RequiredTraitListener(name="bar", notify=False),
                observe.MetadataTraitListener(
                    notify=True,
                    metadata_name="public",
                    include=True,
                ),
            ),
            remove=False,
            dispatch="same",
        )

        # sanity check
        foo.bar.age += 1
        self.assertEqual(mock_obj.call_count, 1)
        mock_obj.reset_mock()

        # Remove the path, but create a new instance of `ListenerPath`
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe.RequiredTraitListener(name="bar", notify=False),
                observe.MetadataTraitListener(
                    notify=True,
                    metadata_name="public",
                    include=True,
                ),
            ),
            remove=True,
            dispatch="same",
        )

        # when
        foo.bar.age += 1

        # then
        mock_obj.assert_not_called()

        # when
        foo.bar = Bar()
        foo.bar.age += 1

        # then
        # This tests the ListenerChangeNotifier is cleaned up
        # properly.
        mock_obj.assert_not_called()


class TestMaintainingListener(unittest.TestCase):
    # Test listeners being persisted for new objects, and removed
    # for old objects.

    def test_two_paths_from_same_item(self):

        class Bar(HasTraits):

            age = Int()

            score = Int()

        class Foo(HasTraits):

            bar = Instance(Bar())

        foo = Foo(bar=Bar())

        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe.RequiredTraitListener(name="bar", notify=False),
                observe.RequiredTraitListener(name="age", notify=True),
            ),
            remove=False,
            dispatch="same",
        )
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe.RequiredTraitListener(name="bar", notify=False),
                observe.RequiredTraitListener(name="score", notify=True),
            ),
            remove=False,
            dispatch="same",
        )

        # sanity check...
        foo.bar.age += 1
        self.assertEqual(mock_obj.call_count, 1)
        mock_obj.reset_mock()
        foo.bar.score += 1
        self.assertEqual(mock_obj.call_count, 1)

        # when
        foo.bar = Bar()

        # then
        mock_obj.reset_mock()
        foo.bar.age += 1
        self.assertEqual(mock_obj.call_count, 1)
        mock_obj.reset_mock()
        foo.bar.score += 1
        self.assertEqual(mock_obj.call_count, 1)

    def test_two_paths_remove_nested_listener(self):

        class Baz(HasTraits):

            age = Int()

            score = Int()

        class Bar(HasTraits):

            baz = Instance(Baz())

        class Foo(HasTraits):

            bar = Instance(Bar())

        foo = Foo(bar=Bar(baz=Baz()))

        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe.RequiredTraitListener(name="bar", notify=False),
                observe.RequiredTraitListener(name="baz", notify=False),
                observe.RequiredTraitListener(name="age", notify=True),
            ),
            remove=False,
            dispatch="same",
        )
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe.RequiredTraitListener(name="bar", notify=False),
                observe.RequiredTraitListener(name="baz", notify=False),
                observe.RequiredTraitListener(name="score", notify=True),
            ),
            remove=False,
            dispatch="same",
        )

        # sanity check
        foo.bar.baz.age += 1
        self.assertEqual(mock_obj.call_count, 1)
        mock_obj.reset_mock()
        foo.bar.baz.score += 1
        self.assertEqual(mock_obj.call_count, 1)
        mock_obj.reset_mock()

        # when
        old_bar = foo.bar
        foo.bar = Bar(baz=Baz())

        # then... when
        old_bar.baz.age += 1
        old_bar.baz.score += 1
        old_bar.baz = Baz()
        old_bar.baz.age += 1
        old_bar.baz.score += 1

        # then
        mock_obj.assert_not_called()

    def test_two_paths_remove_change_notifier(self):
        # test when a listener path is removed, replacing
        # a parent object does not resurrect the nested
        # listeners.
        class Bar(HasTraits):

            age = Int()

            score = Int()

        class Foo(HasTraits):

            bar = Instance(Bar())

        foo = Foo(bar=Bar())

        # add two paths
        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe.RequiredTraitListener(name="bar", notify=False),
                observe.RequiredTraitListener(name="age", notify=True),
            ),
            remove=False,
            dispatch="same",
        )
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe.RequiredTraitListener(name="bar", notify=False),
                observe.RequiredTraitListener(name="score", notify=True),
            ),
            remove=False,
            dispatch="same",
        )

        # remove the last one, with a new instance of ListenerPath that
        # compares equal to the last one.
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe.RequiredTraitListener(name="bar", notify=False),
                observe.RequiredTraitListener(name="score", notify=True),
            ),
            remove=True,
            dispatch="same",
        )
        # sanity check...
        foo.bar.age += 1
        self.assertEqual(mock_obj.call_count, 1)
        mock_obj.reset_mock()
        foo.bar.score += 1
        mock_obj.assert_not_called()

        # when
        foo.bar = Bar()

        # then
        foo.bar.age += 1
        self.assertEqual(mock_obj.call_count, 1)
        mock_obj.reset_mock()

        foo.bar.score += 1
        mock_obj.assert_not_called()


class TestTraitAdded(unittest.TestCase):

    def test_add_trait_with_name(self):

        class Foo(HasTraits):
            pass

        foo = Foo()

        mock_obj = mock.Mock()

        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath(
                observe.OptionalTraitListener(name="a", notify=True),
            ),
            remove=False,
            dispatch="same",
        )
        foo.add_trait("a", Str())
        mock_obj.assert_not_called()

        foo.a = "1"

        self.assertEqual(mock_obj.call_count, 1)
        mock_obj.reset_mock()

        # The observer is for `foo` only
        foo2 = Foo()
        foo2.add_trait("a", Str())
        foo2.a = "2"
        mock_obj.assert_not_called()

    def test_add_trait_with_metadata(self):

        class Foo(HasTraits):
            pass

        foo = Foo()

        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe._FilteredTraitListener(
                    notify=True,
                    filter=lambda name, trait: getattr(trait, "public", False),
                ),
            ),
            remove=False,
            dispatch="same",
        )

        foo.add_trait("a", Str(public=True))
        foo.a = "abc"

        self.assertEqual(mock_obj.call_count, 1)
        mock_obj.reset_mock()

        foo.add_trait("b", Str(public=True))
        foo.b = "abc"

        self.assertEqual(mock_obj.call_count, 1)

    def test_add_trait_in_nested_object(self):

        class Foo(HasTraits):
            pass

        foo = Foo()
        mock_obj = mock.Mock()

        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe.OptionalTraitListener(name="bar", notify=True),
                observe.OptionalTraitListener(name="baz", notify=True),
                observe.OptionalTraitListener(name="age", notify=True),
            ),
            remove=False,
            dispatch="same",
        )

        foo.add_trait("bar", Instance(Foo, ()))
        mock_obj.assert_not_called()

        foo.bar = Foo()
        self.assertEqual(mock_obj.call_count, 1)
        mock_obj.reset_mock()

        foo.bar.add_trait("baz", Instance(Foo, ()))
        mock_obj.assert_not_called()

        foo.bar.baz.add_trait("age", Int())
        mock_obj.assert_not_called()

        foo.bar.baz.age += 1
        self.assertEqual(mock_obj.call_count, 1)
        ((event, ), _), = mock_obj.call_args_list
        self.assertIs(event.object, foo.bar.baz)
        self.assertEqual(event.name, "age")
        self.assertEqual(event.old, 0)
        self.assertEqual(event.new, 1)

    def test_remove_trait_added_listeners(self):

        class Foo(HasTraits):
            pass

        foo = Foo()
        mock_obj = mock.Mock()

        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe.MetadataTraitListener(
                    metadata_name="public", notify=True, include=True
                ),
                observe.MetadataTraitListener(
                    metadata_name="public", notify=True, include=True
                ),
                observe.MetadataTraitListener(
                    metadata_name="public", notify=True, include=True
                ),
            ),
            remove=False,
            dispatch="same",
        )

        # Now add one of the traits.
        foo.add_trait("bar", Instance(Foo, (), public=True))
        foo.bar.add_trait("baz", Instance(Foo, (), public=True))
        mock_obj.assert_not_called()
        foo.bar.baz = Foo()
        self.assertEqual(mock_obj.call_count, 1)
        mock_obj.reset_mock()

        # Now remove the listener.
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe.MetadataTraitListener(
                    metadata_name="public", notify=True, include=True
                ),
                observe.MetadataTraitListener(
                    metadata_name="public", notify=True, include=True
                ),
                observe.MetadataTraitListener(
                    metadata_name="public", notify=True, include=True
                ),
            ),
            remove=True,
            dispatch="same",
        )

        # Now add the rest of the traits
        foo.bar.baz.add_trait("age", Int(public=True))
        mock_obj.assert_not_called()

        # when
        foo.bar.baz.age += 1

        # then
        # should not fire as listener is removed
        mock_obj.assert_not_called()

    def test_trait_added_listener_with_metadata(self):
        # Test trait_added with metadata listener

        class Foo(HasTraits):
            pass

        foo = Foo()
        mock_obj = mock.Mock()

        # Add the listener
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe.MetadataTraitListener(
                    metadata_name="updated",
                    notify=True,
                    include=True,
                ),
            ),
            remove=False,
            dispatch="same",
        )

        foo.add_trait("age", Int(updated=True))
        mock_obj.assert_not_called()
        foo.age += 1
        self.assertEqual(mock_obj.call_count, 1)

    def test_add_trait_selective(self):
        # Test filtering on the added trait

        class Foo(HasTraits):
            pass

        foo = Foo()
        mock_obj = mock.Mock()

        # Add the listener
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe.MetadataTraitListener(
                    metadata_name="name", notify=True, include=True)
            ),
            remove=False,
            dispatch="same",
        )

        # Not the listened trait
        foo.add_trait("age", Int(updated=True))

        foo.age += 1

        mock_obj.assert_not_called()

    def test_add_trait_with_list(self):

        class Bar(HasTraits):
            pass

        class Foo(HasTraits):
            pass

        foo = Foo()
        mock_obj = mock.Mock()
        observe.observe(
            object=foo,
            callback=mock_obj,
            path=observe.ListenerPath.from_nodes(
                observe.OptionalTraitListener(
                    name="bars", notify=False,
                ),
                observe.ListItemListener(notify=False),
                observe.OptionalTraitListener(
                    name="age", notify=True,
                )
            ),
            remove=False,
            dispatch="same",
        )

        # now add traits
        foo.add_trait("bars", List(Bar()))
        bar = Bar()
        foo.bars = [bar]
        bar.add_trait("age", Int())
        mock_obj.assert_not_called()

        # when
        bar.age += 1

        # then
        self.assertEqual(mock_obj.call_count, 1)
        mock_obj.reset_mock()

        # when
        # this trait is not listened to
        bar.add_trait("name", Str())
        bar.name = "Joe"

        # then
        mock_obj.assert_not_called()



class TestPathEqual(unittest.TestCase):

    def test_simple_named_path(self):

        path1 = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="a", notify=False),
            observe.OptionalTraitListener(name="b", notify=True),
        )
        path2 = observe.ListenerPath.from_nodes(
            observe.RequiredTraitListener(name="a", notify=False),
            observe.OptionalTraitListener(name="b", notify=True),
        )
        self.assertEqual(path1, path2)

    def test_simple_branched_named_path(self):
        path1 = observe.ListenerPath(
            node=observe.RequiredTraitListener(name="a", notify=False),
            nexts=[
                observe.ListenerPath(
                    observe.OptionalTraitListener(name="b", notify=True)
                ),
                observe.ListenerPath(
                    observe.OptionalTraitListener(name="c", notify=True)
                ),
            ],
        )
        # The nexts are in different order
        path2 = observe.ListenerPath(
            node=observe.RequiredTraitListener(name="a", notify=False),
            nexts=[
                observe.ListenerPath(
                    observe.OptionalTraitListener(name="c", notify=True)
                ),
                observe.ListenerPath(
                    observe.OptionalTraitListener(name="b", notify=True)
                ),
            ],
        )

        self.assertEqual(path1, path2)


if __name__ == "__main__":
    unittest.main()
