# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest
from unittest import mock

from traits.has_traits import HasTraits
from traits.observation._testing import (
    call_add_or_remove_notifiers,
    create_graph,
    DummyNotifier,
    DummyObserver,
)
from traits.observation._trait_added_observer import (
    _RestrictedNamedTraitObserver,
    TraitAddedObserver,
)
from traits.trait_types import Str


def create_observer(**kwargs):
    values = dict(
        match_func=mock.Mock(),
        optional=False,
    )
    values.update(kwargs)
    return TraitAddedObserver(**values)


class DummyMatchFunc:
    """ A callable to be used as TraitAddedObserver.match_func
    """

    def __init__(self, return_value):
        self.return_value = return_value

    def __call__(self, name, trait):
        return self.return_value

    def __eq__(self, other):
        return self.return_value == other.return_value

    def __hash__(self):
        return hash(self.return_value)


class TestTraitAddedObserverEqualHash(unittest.TestCase):
    """ Tests for TraitAddedObserver __eq__ and __hash__ methods.
    """

    def test_not_equal_match_func(self):
        observer1 = TraitAddedObserver(match_func=mock.Mock(), optional=True)
        observer2 = TraitAddedObserver(match_func=mock.Mock(), optional=True)
        self.assertNotEqual(observer1, observer2)

    def test_not_equal_optional(self):
        match_func = mock.Mock()
        observer1 = TraitAddedObserver(match_func=match_func, optional=False)
        observer2 = TraitAddedObserver(match_func=match_func, optional=True)
        self.assertNotEqual(observer1, observer2)

    def test_equal_match_func_optional(self):
        # If two match_func compare equally and optional is the same
        # then they are the same.
        observer1 = TraitAddedObserver(
            match_func=DummyMatchFunc(return_value=True),
            optional=False,
        )
        observer2 = TraitAddedObserver(
            match_func=DummyMatchFunc(return_value=True),
            optional=False,
        )
        self.assertEqual(observer1, observer2)
        self.assertEqual(hash(observer1), hash(observer2))

    def test_not_equal_type(self):
        match_func = mock.Mock()
        observer1 = TraitAddedObserver(
            match_func=match_func,
            optional=False,
        )
        imposter = mock.Mock()
        imposter.match_func = match_func
        imposter.optional = False
        self.assertNotEqual(observer1, imposter)

    def test_notify_is_false(self):
        observer = create_observer()
        self.assertFalse(
            observer.notify,
            "TraitAddedObserver.notify should be always false.",
        )


class TestRestrictedNamedTraitObserverEqualityHash(unittest.TestCase):
    """ Test _RestrictedNamedTraitObserver.__eq__ and __hash__ """

    def test_equality_name_and_observer(self):
        wrapped_observer = DummyObserver()
        observer1 = _RestrictedNamedTraitObserver(
            name="name", wrapped_observer=wrapped_observer)
        observer2 = _RestrictedNamedTraitObserver(
            name="name", wrapped_observer=wrapped_observer)
        self.assertEqual(observer1, observer2)
        self.assertEqual(hash(observer1), hash(observer2))

    def test_not_equal_name(self):
        wrapped_observer = DummyObserver()
        observer1 = _RestrictedNamedTraitObserver(
            name="name", wrapped_observer=wrapped_observer)
        observer2 = _RestrictedNamedTraitObserver(
            name="other", wrapped_observer=wrapped_observer)
        self.assertNotEqual(observer1, observer2)

    def test_not_equal_observer(self):
        observer1 = _RestrictedNamedTraitObserver(
            name="name", wrapped_observer=DummyObserver())
        observer2 = _RestrictedNamedTraitObserver(
            name="name", wrapped_observer=DummyObserver())
        self.assertNotEqual(observer1, observer2)


class TestRestrictedNamedTraitObserverWithWrappedObserver(unittest.TestCase):
    """ Test the quantities inherited from the wrapped observer."""

    def test_notify_inherited(self):
        wrapped_observer = DummyObserver(notify=False)
        observer = _RestrictedNamedTraitObserver(
            name="name", wrapped_observer=wrapped_observer)
        self.assertEqual(observer.notify, wrapped_observer.notify)

    def test_notifier_inherited(self):
        notifier = DummyNotifier()
        wrapped_observer = DummyObserver(notifier=notifier)
        observer = _RestrictedNamedTraitObserver(
            name="name", wrapped_observer=wrapped_observer)
        self.assertEqual(
            observer.get_notifier(None, None, None),
            notifier,
        )

    def test_maintainer_inherited(self):
        maintainer = DummyNotifier()
        wrapped_observer = DummyObserver(maintainer=maintainer)
        observer = _RestrictedNamedTraitObserver(
            name="name", wrapped_observer=wrapped_observer)
        self.assertEqual(
            observer.get_maintainer(None, None, None, None),
            maintainer,
        )


# -----------------------------------
# Integration tests with HasTraits
# -----------------------------------

class DummyHasTraitsClass(HasTraits):

    def dummy_method(self):
        pass


class TestTraitAddedObserverIterObservables(unittest.TestCase):
    """ Test sanity checks in iter_observables. """

    def test_iter_observables_get_trait_added_ctrait(self):
        observer = create_observer()
        instance = DummyHasTraitsClass()

        actual, = list(observer.iter_observables(instance))
        self.assertEqual(actual, instance._trait("trait_added", 2))

    def test_iter_observables_ignore_incompatible_object_if_optional(self):
        observer = create_observer(optional=True)

        actual = list(observer.iter_observables(None))
        self.assertEqual(actual, [])

    def test_iter_observables_error_incompatible_object_if_required(self):
        observer = create_observer(optional=False)

        with self.assertRaises(ValueError) as exception_cm:
            list(observer.iter_observables(None))

        self.assertIn(
            "Unable to observe 'trait_added'", str(exception_cm.exception))


class TestTraitAddedObserverIterObjects(unittest.TestCase):
    """ Test iter_objects yields nothing. """

    def test_iter_objects_yields_nothing(self):
        observer = create_observer()
        actual = list(observer.iter_objects(None))
        self.assertEqual(actual, [])


class TestTraitAddedObserverNotifications(unittest.TestCase):
    """ Test the core logic for maintaining downstream observers
    when a trait is added.
    """

    def setUp(self):

        def match_func(name, trait):
            return name.startswith("good_")

        self.observer = TraitAddedObserver(
            match_func=match_func,
            optional=False,
        )

    def test_maintainer_trait_added(self):
        # Test the maintainer is added for the trait_added event.
        instance = DummyHasTraitsClass()
        notifier = DummyNotifier()
        maintainer = DummyNotifier()
        graph = create_graph(
            self.observer,
            DummyObserver(
                notify=True,
                notifier=notifier,
                maintainer=maintainer,
            ),
            DummyObserver(),  # to get maintainer in
        )
        call_add_or_remove_notifiers(
            object=instance,
            handler=instance.dummy_method,
            target=instance,
            graph=graph,
            remove=False,
        )

        # when
        instance.add_trait("good_name", Str())

        # then
        # the maintainer will have added a notifier because notify flag
        # is set to true on the single observer being maintained.
        notifiers = instance._trait("good_name", 2)._notifiers(True)
        self.assertIn(notifier, notifiers)
        self.assertIn(maintainer, notifiers)

        # when
        instance.add_trait("bad_name", Str())

        # then
        notifiers = instance._trait("bad_name", 2)._notifiers(True)
        self.assertNotIn(notifier, notifiers)
        self.assertNotIn(maintainer, notifiers)

    def test_maintainer_keep_notify_flag(self):
        # Test the maintainer will maintain the notify flag for the root
        # observer in the subgraph.
        instance = DummyHasTraitsClass()
        notifier = DummyNotifier()
        graph = create_graph(
            self.observer,
            DummyObserver(
                notify=False,
                notifier=notifier,
            ),
        )
        handler = mock.Mock()
        call_add_or_remove_notifiers(
            object=instance,
            handler=handler,
            target=instance,
            graph=graph,
            remove=False,
        )

        # when
        instance.add_trait("good_name", Str())

        # then
        # notify flag is set to false, so there are no notifiers added.
        notifiers = instance._trait("good_name", 2)._notifiers(True)
        self.assertNotIn(notifier, notifiers)
