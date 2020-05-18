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

from traits.api import HasTraits, Int
from traits.observers._filtered_trait_observer import FilteredTraitObserver
from traits.observers._metadata_filter import MetadataFilter
from traits.observers._testing import (
    call_add_or_remove_notifiers,
    create_graph,
)
from traits.trait_types import Int


class TestMetadataFilter(unittest.TestCase):
    """ Test the behaviour of the MetadataFilter """

    def setUp(self):

        def value_is_not_none(value):
            return value is not None

        self.value_is_not_none = value_is_not_none

    def test_value_is_a_callable(self):
        metadata_filter = MetadataFilter(
            metadata_name="name",
            value=self.value_is_not_none,
        )
        self.assertTrue(
            metadata_filter("name", Int(name=True).as_ctrait()),
            "Expected the filter to return true"
        )
        self.assertFalse(
            metadata_filter("name", Int(name=None).as_ctrait()),
            "Expected the filter to return false"
        )

    def test_skip_undefined_metadata(self):
        # Handle when a value is not defined.
        metadata_filter = MetadataFilter(
            metadata_name="name",
            value=self.value_is_not_none,
        )

        self.assertFalse(
            metadata_filter("name", Int().as_ctrait()),
            "Expected the filter to return false"
        )

    def test_filter_equality(self):
        filter1 = MetadataFilter(
            metadata_name="name",
            value=self.value_is_not_none,
        )
        filter2 = MetadataFilter(
            metadata_name="name",
            value=self.value_is_not_none,
        )
        self.assertEqual(filter1, filter2)
        self.assertEqual(hash(filter1), hash(filter2))

    def test_filter_not_equal_name_different(self):
        filter1 = MetadataFilter(
            metadata_name="number",
            value=self.value_is_not_none,
        )
        filter2 = MetadataFilter(
            metadata_name="name",
            value=self.value_is_not_none,
        )
        self.assertNotEqual(filter1, filter2)

    def test_filter_not_equal_value_different(self):
        # the value filters do not compare equally
        filter1 = MetadataFilter(
            metadata_name="name",
            value=lambda v: v is not None,
        )
        filter2 = MetadataFilter(
            metadata_name="name",
            value=lambda v: v is not None,
        )
        self.assertNotEqual(filter1, filter2)

    def test_filter_not_equal_different_type(self):
        filter1 = MetadataFilter(
            metadata_name="name",
            value=self.value_is_not_none,
        )
        imposter = mock.Mock()
        imposter.metadata_name = "name"
        imposter.value = self.value_is_not_none
        self.assertNotEqual(imposter, filter1)

    def test_repr_value(self):
        metadata_filter = MetadataFilter(
            metadata_name="name",
            value=self.value_is_not_none,
        )
        actual = repr(metadata_filter)
        self.assertEqual(
            actual,
            "MetadataFilter(metadata_name='name', value=value_is_not_none)"
        )


class TestWithFilteredTraitObserver(unittest.TestCase):
    """ Test MetadataFilter with FilteredTraitObserver and HasTraits. """

    def test_filter_metadata(self):

        class Person(HasTraits):
            age = Int(status="private")
            n_jobs = Int(status="public")
            n_children = Int()   # no metadata

        observer = FilteredTraitObserver(
            filter=MetadataFilter(
                metadata_name="status",
                value=lambda value: value == "public",
            ),
            notify=True,
        )
        person = Person()
        handler = mock.Mock()
        call_add_or_remove_notifiers(
            object=person,
            graph=create_graph(observer),
            handler=handler,
        )

        # when
        person.n_jobs += 1

        # then
        self.assertEqual(handler.call_count, 1)
        handler.reset_mock()

        # when
        person.age += 1

        # then
        self.assertEqual(handler.call_count, 0)

        # when
        person.n_children += 1

        # then
        self.assertEqual(handler.call_count, 0)
