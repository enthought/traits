import contextlib
import unittest
from unittest import mock

import observe

from traits.api import HasTraits, Int
from trait_types import List


class TestList(unittest.TestCase):

    class Bar(HasTraits):

        age = Int()

    class Foo(HasTraits):

        l = List()

    def test_observer_is_quiet(self):
        # The callback is not called when we merely add an observer
        item_path = observe.ListenerPath(
            node=observe.RequiredTraitListener(name="l", notify=False),
            next=observe.ListenerPath(
                node=observe.ListItemListener(notify=True)
            )
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
        age_path = observe.ListenerPath(
            node=observe.RequiredTraitListener(name="l", notify=False),
            next=observe.ListenerPath(
                node=observe.ListItemListener(notify=False),
                next=observe.ListenerPath(
                    node=observe.RequiredTraitListener(
                        name="age", notify=True),
                )
            )
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
        item_path = observe.ListenerPath(
            node=observe.RequiredTraitListener(name="l", notify=False),
            next=observe.ListenerPath(
                node=observe.ListItemListener(notify=True)
            )
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
        item_path = observe.ListenerPath(
            node=observe.RequiredTraitListener(name="l", notify=False),
            next=observe.ListenerPath(
                node=observe.ListItemListener(notify=True)
            )
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
        age_path = observe.ListenerPath(
            node=observe.RequiredTraitListener(name="l", notify=False),
            next=observe.ListenerPath(
                node=observe.ListItemListener(notify=False),
                next=observe.ListenerPath(
                    node=observe.RequiredTraitListener(
                        name="age", notify=True),
                )
            )
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

    def test_multiple_identical_object_in_list(self):
        # enthought/traits#237
        age_path = observe.ListenerPath(
            node=observe.RequiredTraitListener(name="l", notify=False),
            next=observe.ListenerPath(
                node=observe.ListItemListener(notify=False),
                next=observe.ListenerPath(
                    node=observe.RequiredTraitListener(
                        name="age", notify=True),
                )
            )
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

        bar = self.Bar()
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

    def test_mutate_removed_object(self):
        # Test when an object is removed from the list,
        # no change events are fired
        age_path = observe.ListenerPath(
            node=observe.RequiredTraitListener(name="l", notify=False),
            next=observe.ListenerPath(
                node=observe.ListItemListener(notify=False),
                next=observe.ListenerPath(
                    node=observe.RequiredTraitListener(
                        name="age", notify=True),
                )
            )
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
        age_path = observe.ListenerPath(
            node=observe.RequiredTraitListener(name="l", notify=False),
            next=observe.ListenerPath(
                node=observe.ListItemListener(notify=False),
                next=observe.ListenerPath(
                    node=observe.RequiredTraitListener(
                        name="age", notify=True),
                )
            )
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




if __name__ == "__main__":
    unittest.main()
