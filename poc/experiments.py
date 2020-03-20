import contextlib
import unittest
from unittest import mock

import observe

from traits.api import HasTraits, Int, Instance, Str
from trait_types import List

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

        mock_obj.assert_called_once()
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

        mock_obj.assert_called_once()
        ((event, ), _), = mock_obj.call_args_list
        self.assertIs(event.old, f.l)
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

        mock_obj.assert_called_once()
        ((event, ), _), = mock_obj.call_args_list
        self.assertIs(event.old, f.l)
        self.assertIs(event.new, f.l)
        self.assertEqual(event.removed, [])
        self.assertEqual(event.added, [bar, bar])

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
        mock_obj.assert_called_once()
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
        mock_obj.assert_called_once()

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
        mock_obj.assert_called_once()
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
        # FIXME: Notification should be fired.
        with self.assertRaises(AssertionError):
            mock_obj.assert_called_once()

    def test_implicit_default_list(self):
        # Test when a list attribute is accessed the first time,
        # the default list created will also receive the notifiers.
        list_path = observe.ListenerPath(
            node=observe.RequiredTraitListener(name="l", notify=True),
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
        mock_obj.assert_called_once()
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
        mock_obj.assert_called_once()
        ((event, ), _), = mock_obj.call_args_list
        self.assertIs(event.object, foo)
        self.assertEqual(event.name, "bars")
        self.assertEqual(event.old, [])
        self.assertEqual(event.new, [[1, 2]])

        # when
        mock_obj.reset_mock()
        foo.bars[0].append(3)

        # then
        mock_obj.assert_called_once()
        ((event, ), _), = mock_obj.call_args_list
        # TODO: Is this the right object?
        self.assertEqual(event.object, foo.bars)
        # TODO: Bogus filler, can we remove it?
        self.assertEqual(event.name, "")
        # TODO: Bogus filler again, can we remove it?
        self.assertIs(event.old, foo.bars[0])

        self.assertIs(event.new, foo.bars[0])
        self.assertEqual(event.index, 2)
        self.assertEqual(foo.bars, [[1, 2, 3]])

        # when
        mock_obj.reset_mock()
        foo.bars = [[1, 2]]

        # then
        mock_obj.assert_called_once()

        # when
        mock_obj.reset_mock()
        foo.bars[0] = [3]

        # then
        mock_obj.assert_called_once()

        # when
        self.assertEqual(foo.bars, [[3]])
        mock_obj.reset_mock()
        foo.bars = [[3]]

        # then
        # The values compared equal, despite the inner list being a
        # a different list
        mock_obj.assert_not_called()

        # FIXME: Now the new list does not have the expected notifiers!
        # when
        foo.bars[0] = [4]

        # then
        with self.assertRaises(AssertionError):
            mock_obj.assert_called_once()

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
        mock_obj.assert_called_once()

        # when
        # Reassign to a new list that compares equal.
        self.assertEqual(foo.bars[0], [[1]])
        foo.bars[slice(0, 0)] = [[[1]]]
        self.assertEqual(foo.bars[0], [[1]])

        mock_obj.reset_mock()
        foo.bars[0][0].append(2)

        # then
        # FIXME: One notification should be fired
        with self.assertRaises(AssertionError):
            mock_obj.assert_called_once()


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
        mock_obj.assert_called_once()

        # when
        mock_obj.reset_mock()
        parent.children.append(second_child)

        # then
        mock_obj.assert_called_once()

        # when
        mock_obj.reset_mock()
        second_child.value += 1

        # then
        mock_obj.assert_called_once()


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
        mock_obj.assert_called_once()
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
        mock_obj.assert_called_once()
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
        mock_obj.assert_called_once()

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
        mock_obj.assert_called_once()


class TestFilteredTrait(unittest.TestCase):

    def test_filter_metadata(self):

        class Foo(HasTraits):

            age = Int(public=False)
            name = Str(public=True)
            gender = Str(public=True)

        path = observe.ListenerPath.from_nodes(
            observe.FilteredTraitListener(notify=True, filter=lambda _, trait: trait.public),
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
        mock_obj.assert_called_once()
        ((event, ), _), = mock_obj.call_args_list
        self.assertIs(event.object, foo)
        self.assertEqual(event.name, "name")
        self.assertEqual(event.old, "John")
        self.assertEqual(event.new, "Jim")

        # when
        mock_obj.reset_mock()
        foo.gender = "unknown"

        # then
        mock_obj.assert_called_once()
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
            observe.FilteredTraitListener(notify=False, filter=lambda _, trait: trait.public),
            observe.FilteredTraitListener(notify=True, filter=lambda _, trait: trait.public),
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
        mock_obj.assert_called_once()
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


if __name__ == "__main__":
    unittest.main()
