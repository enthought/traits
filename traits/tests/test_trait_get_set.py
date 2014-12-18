#  Test the 'trait_set', 'trait_get' interface to
#  the HasTraits class.
#
#  Copyright (c) 2014, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  License included in /LICENSE.txt and may be redistributed only under the
#  conditions described in the aforementioned license.  The license is also
#  available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
from __future__ import absolute_import

from contextlib import contextmanager
import logging

import traits.has_traits
from traits.testing.unittest_tools import unittest, UnittestTools

from ..api import HasTraits, Str, Int


class TraitsObject(HasTraits):

    string = Str
    integer = Int


class ListHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)
        self.records = []

    def emit(self, record):
        self.records.append(record)


@contextmanager
def catch_logs(module_name):
    logger = logging.getLogger(module_name)
    logger.propagate = False
    handler = ListHandler()
    logger.addHandler(handler)
    try:
        yield handler
    finally:
        logger.removeHandler(handler)
        logger.propagate = True


class TestTraitGet(UnittestTools, unittest.TestCase):

    def test_trait_set(self):
        obj = TraitsObject()
        obj.trait_set(string='foo')
        self.assertEqual(obj.string, 'foo')
        self.assertEqual(obj.integer, 0)

    def test_trait_get(self):
        obj = TraitsObject()
        obj.trait_set(string='foo')
        values = obj.trait_get('string', 'integer')
        self.assertEqual(values, {'string': 'foo', 'integer': 0})

    def test_trait_set_deprecated(self):
        obj = TraitsObject()

        with self.assertNotDeprecated():
            obj.trait_set(integer=1)

        with self.assertDeprecated():
            obj.set(string='foo')

        self.assertEqual(obj.string, 'foo')
        self.assertEqual(obj.integer, 1)

    def test_trait_get_deprecated(self):
        obj = TraitsObject()
        obj.string = 'foo'
        obj.integer = 1

        with self.assertNotDeprecated():
            values = obj.trait_get('integer')
        self.assertEqual(values, {'integer': 1})

        with self.assertDeprecated():
            values = obj.get('string')
        self.assertEqual(values, {'string': 'foo'})
