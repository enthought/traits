# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import io
import pickle
import unittest
from unittest import mock
import weakref

from traits.api import (
    Any,
    Bool,
    cached_property,
    HasTraits,
    Instance,
    Int,
    List,
    observe,
    on_trait_change,
    Property,
    Str,
)
from traits.trait_base import Undefined
from traits.observation.api import (
    trait,
    pop_exception_handler,
    push_exception_handler,
)


class HasProperty(HasTraits):

    output_buffer = Any()

    def __value_get(self):
        return self.__dict__.get("_value", 0)

    def __value_set(self, value):
        old_value = self.__dict__.get("_value", 0)
        if value != old_value:
            self._value = value
            self.trait_property_changed("value", old_value, value)

    value = Property(__value_get, __value_set)


class HasPropertySubclass(HasProperty):
    def _value_changed(self, value):
        self.output_buffer.write(value)


class TestPropertyNotifications(unittest.TestCase):
    def test_property_notifications(self):
        output_buffer = io.StringIO()

        test_obj = HasPropertySubclass(output_buffer=output_buffer)
        test_obj.value = "value_1"
        self.assertEqual(output_buffer.getvalue(), "value_1")

        test_obj.value = "value_2"
        self.assertEqual(output_buffer.getvalue(), "value_1value_2")


# Integration test for Property notifications via 'observe' / 'depends_on'


class PersonInfo(HasTraits):

    age = Int()

    gender = Str()


class ClassWithInstanceDefaultInit(HasTraits):

    info_without_default = Instance(PersonInfo)

    list_of_infos = List(Instance(PersonInfo), comparison_mode=1)

    sample_info = Instance(PersonInfo)

    sample_info_default_computed = Bool()

    def _sample_info_default(self):
        self.sample_info_default_computed = True
        return PersonInfo(age=self.info_without_default.age)

    info_with_default = Instance(PersonInfo)

    info_with_default_computed = Bool()

    def _info_with_default_default(self):
        self.info_with_default_computed = True
        return PersonInfo(age=12)


class ClassWithPropertyObservesDefault(ClassWithInstanceDefaultInit):
    """ Dummy class for testing property with an observer on an extended
    attribute. 'info_with_default has a default initializer.
    To be compared with the next class using depends_on
    """

    extended_age = Property(observe="info_with_default.age")

    extended_age_n_calculations = Int()

    def _get_extended_age(self):
        self.extended_age_n_calculations += 1
        return self.info_with_default.age


class ClassWithPropertyDependsOnDefault(ClassWithInstanceDefaultInit):
    """ Dummy class for testing property with an observer on an extended
    attribute. 'info_with_default' has a default initializer.
    """

    extended_age = Property(depends_on="info_with_default.age")

    extended_age_n_calculations = Int()

    def _get_extended_age(self):
        self.extended_age_n_calculations += 1
        return self.info_with_default.age


class ClassWithPropertyObservesInit(ClassWithInstanceDefaultInit):
    """ Dummy class for testing property with an observer on an extended
    attribute. sample_info has a default value depending on
    'info_without_default'. The value of 'info_without_default' is provided
    by __init__.
    To be compared with the next class using depends_on.
    """

    extended_age = Property(observe="sample_info.age")

    extended_age_n_calculations = Int()

    def _get_extended_age(self):
        self.extended_age_n_calculations += 1
        return self.sample_info.age


class ClassWithPropertyDependsOnInit(ClassWithInstanceDefaultInit):
    # This class cannot be instantiated.
    # enthought/traits#709

    extended_age = Property(depends_on="sample_info.age")

    def _get_extended_age(self):
        return self.sample_info.age


class ClassWithPropertyMultipleObserves(PersonInfo):
    """ Dummy class to test observing multiple values.
    """

    computed_value = Property(observe=[trait("age"), trait("gender")])

    computed_value_n_calculations = Int()

    def _get_computed_value(self):
        self.computed_value_n_calculations += 1
        return len(self.gender) + self.age


class ClassWithPropertyMultipleDependsOn(PersonInfo):
    """ Dummy class using 'depends_on', to be compared with the one above.
    """

    computed_value = Property(depends_on=["age", "gender"])

    computed_value_n_calculations = Int()

    def _get_computed_value(self):
        self.computed_value_n_calculations += 1
        return len(self.gender) + self.age


class ClassWithPropertyObservesItems(ClassWithInstanceDefaultInit):
    """ Dummy class to test property observing container items"""

    discounted = Property(
        Bool(), observe=trait("list_of_infos").list_items().trait("age"))

    discounted_n_calculations = Int()

    def _get_discounted(self):
        self.discounted_n_calculations += 1
        return any(info.age > 70 for info in self.list_of_infos)


class ClassWithPropertyDependsOnItems(ClassWithInstanceDefaultInit):
    """ Dummy class using depends_on to be compared with the one using
    observe."""

    discounted = Property(Bool(), depends_on="list_of_infos.age")

    discounted_n_calculations = Int()

    def _get_discounted(self):
        self.discounted_n_calculations += 1
        return any(info.age > 70 for info in self.list_of_infos)


class ClassWithPropertyObservesWithCache(PersonInfo):

    discounted = Property(Bool(), observe="age")

    discounted_n_calculations = Int()

    @cached_property
    def _get_discounted(self):
        self.discounted_n_calculations += 1
        return self.age > 10


class ClassWithPropertyObservesDecorated(PersonInfo):
    """ Dummy class to test property with observers setup at init time."""

    discounted = Property(Bool(), observe="age")

    discounted_n_calculations = Int()

    def _get_discounted(self):
        self.discounted_n_calculations += 1
        return self.age > 60

    discounted_events = List()

    @observe("discounted")
    def discounted_updated(self, event):
        self.discounted_events.append(event)


class ClassWithPropertyDependsOnDecorated(PersonInfo):
    """ Dummy class to test property with depends_on and on_trait_change
    setup at init time."""

    discounted = Property(Bool(), depends_on="age")

    discounted_n_calculations = Int()

    def _get_discounted(self):
        self.discounted_n_calculations += 1
        return self.age > 60

    discounted_events = List()

    @on_trait_change("discounted")
    def discounted_updated(self, event):
        self.discounted_events.append(event)


class ClassWithPropertyMissingGetter(PersonInfo):
    """ Dummy class to test property that does not have getter/setter.
    """

    discounted = Property(Bool(), observe="age")


class ClassWithPropertyTraitNotFound(HasTraits):
    """ Dummy class to test error, prevent issues like enthought/traits#447
    """

    person = Instance(PersonInfo)

    last_name = Property(observe="person.last_name")  # last_name not defined


class TestHasTraitsPropertyObserves(unittest.TestCase):
    """ Tests Property notifications using 'observe', and compared the
    behavior with 'depends_on'
    """

    def setUp(self):
        push_exception_handler(reraise_exceptions=True)
        self.addCleanup(pop_exception_handler)

    def test_property_observe_extended_trait(self):
        instance_observe = ClassWithPropertyObservesDefault()
        handler_observe = mock.Mock()
        instance_observe.observe(handler_observe, "extended_age")

        # sanity check against depends_on
        instance_depends_on = ClassWithPropertyDependsOnDefault()
        handler_otc = mock.Mock()
        instance_depends_on.on_trait_change(
            get_otc_handler(handler_otc), "extended_age"
        )
        instances = [instance_observe, instance_depends_on]
        handlers = [handler_observe, handler_otc]

        for instance, handler in zip(instances, handlers):
            with self.subTest(instance=instance, handler=handler):
                # when
                instance.info_with_default.age = 70
                # then
                self.assertEqual(handler.call_count, 1)
                self.assertEqual(instance.extended_age_n_calculations, 1)

    def test_property_observe_does_not_fire_default(self):
        instance_observe = ClassWithPropertyObservesDefault()
        handler_observe = mock.Mock()
        instance_observe.observe(handler_observe, "extended_age")

        # compared with 'depends_on'
        instance_depends_on = ClassWithPropertyDependsOnDefault()
        instance_depends_on.on_trait_change(
            get_otc_handler(mock.Mock()), "extended_age")

        # then
        # they are different. See enthought/traits#481, #709
        self.assertFalse(instance_observe.info_with_default_computed)
        self.assertTrue(instance_depends_on.info_with_default_computed)

    def test_property_multi_observe(self):
        instance_observe = ClassWithPropertyMultipleObserves()
        handler_observe = mock.Mock()
        instance_observe.observe(handler_observe, "computed_value")
        self.assertEqual(instance_observe.computed_value_n_calculations, 0)

        instance_depends_on = ClassWithPropertyMultipleDependsOn()
        instance_depends_on.on_trait_change(
            get_otc_handler(mock.Mock()), "computed_value")
        self.assertEqual(instance_depends_on.computed_value_n_calculations, 0)

        for instance in [instance_observe, instance_depends_on]:
            with self.subTest(instance=instance):
                # when
                instance.age = 1
                # then
                self.assertEqual(instance.computed_value_n_calculations, 1)
                # when
                instance.gender = "male"
                # then
                self.assertEqual(instance.computed_value_n_calculations, 2)

    def test_property_observe_container(self):
        instance_observe = ClassWithPropertyObservesItems()
        handler_observe = mock.Mock()
        instance_observe.observe(handler_observe, "discounted")

        instance_depends_on = ClassWithPropertyDependsOnItems()
        instance_depends_on.on_trait_change(
            get_otc_handler(mock.Mock()), "discounted")

        for instance in [instance_observe, instance_depends_on]:
            with self.subTest(instance=instance):
                self.assertEqual(instance.discounted_n_calculations, 0)

                instance.list_of_infos.append(PersonInfo(age=30))
                self.assertEqual(instance.discounted_n_calculations, 1)

                instance.list_of_infos[-1].age = 80
                self.assertEqual(instance.discounted_n_calculations, 2)

    def test_property_old_value_uncached(self):
        instance = ClassWithPropertyMultipleObserves()
        handler = mock.Mock()
        instance.observe(handler, "computed_value")

        instance.age = 1

        ((event, ), _), = handler.call_args_list
        self.assertIs(event.object, instance)
        self.assertEqual(event.name, "computed_value")
        self.assertIs(event.old, Undefined)  # property is not cached
        self.assertIs(event.new, 1)

        handler.reset_mock()
        instance.gender = "male"

        ((event, ), _), = handler.call_args_list
        self.assertIs(event.object, instance)
        self.assertEqual(event.name, "computed_value")
        self.assertIs(event.old, Undefined)  # property is not cached
        self.assertIs(event.new, 5)  # len("male") + 1

    def test_property_with_cache(self):
        instance = ClassWithPropertyObservesWithCache()
        handler = mock.Mock()
        instance.observe(handler, "discounted")
        instance.age = 1

        (event, ), _ = handler.call_args_list[-1]
        self.assertIs(event.object, instance)
        self.assertEqual(event.name, "discounted")
        self.assertIs(event.old, Undefined)
        self.assertIs(event.new, False)
        handler.reset_mock()

        instance.age = 80

        (event, ), _ = handler.call_args_list[-1]
        self.assertIs(event.object, instance)
        self.assertEqual(event.name, "discounted")
        self.assertIs(event.old, False)
        self.assertIs(event.new, True)

    def test_property_default_initializer_with_value_in_init(self):
        # With "depends_on", instantiation will fail.
        # enthought/traits#709
        with self.assertRaises(AttributeError):
            ClassWithPropertyDependsOnInit(
                info_without_default=PersonInfo(age=30))

        # With "observe", initialization works.
        instance = ClassWithPropertyObservesInit(
            info_without_default=PersonInfo(age=30)
        )
        handler = mock.Mock()
        instance.observe(handler, "extended_age")
        self.assertFalse(instance.sample_info_default_computed)
        self.assertEqual(instance.sample_info.age, 30)
        self.assertEqual(instance.extended_age, 30)
        # not called because 'sample_info' is still the "default" value.
        self.assertEqual(handler.call_count, 0)

        # when
        instance.sample_info.age = 40

        # then
        self.assertEqual(handler.call_count, 1)

        # sanity check this is consistent with when property is not defined.
        instance_no_property = ClassWithInstanceDefaultInit(
            info_without_default=PersonInfo(age=30)
        )
        self.assertFalse(instance_no_property.sample_info_default_computed)
        self.assertEqual(instance_no_property.sample_info.age, 30)

    def test_property_decorated_observer(self):
        instance_observe = ClassWithPropertyObservesDecorated(age=30)
        instance_depends_on = ClassWithPropertyDependsOnDecorated(age=30)

        for instance in [instance_observe, instance_depends_on]:
            with self.subTest(instance=instance):
                self.assertEqual(len(instance.discounted_events), 1)

    def test_garbage_collectable(self):
        instance = ClassWithPropertyObservesDefault()

        instance_ref = weakref.ref(instance)

        del instance

        self.assertIsNone(instance_ref())

    def test_property_with_no_getter(self):
        instance = ClassWithPropertyMissingGetter()
        try:
            instance.age += 1
        except Exception:
            self.fail(
                "Having property with undefined getter/setter should not "
                "prevent the observed traits from being changed."
            )

    def test_property_with_missing_dependent(self):
        # This will prevent incidents like the one in enthought/traits#447
        instance = ClassWithPropertyTraitNotFound()
        with self.assertRaises(ValueError) as exception_context:
            instance.person = PersonInfo()

        self.assertIn(
            "Trait named 'last_name' not found",
            str(exception_context.exception),
        )

    def test_pickle_has_traits_with_property_observe(self):
        instance = ClassWithPropertyMultipleObserves()

        for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
            serialized = pickle.dumps(instance, protocol=protocol)
            deserialized = pickle.loads(serialized)
            handler = mock.Mock()
            deserialized.observe(handler, "computed_value")
            deserialized.age = 1
            self.assertEqual(handler.call_count, 1)


def get_otc_handler(mock_obj):
    """ Return a callable to be used with on_trait_change, which will
    inspect call signature.

    Parameters
    ----------
    mock_obj : mock.Mock
        Mock object for tracking calls.
    """

    def handler():
        mock_obj()

    return handler
