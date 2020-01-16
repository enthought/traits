# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Unit tests for the Tuple trait type.
"""
import unittest

from traits.tests.tuple_test_mixin import TupleTestMixin
from traits.trait_types import Tuple


class TupleTestCase(TupleTestMixin, unittest.TestCase):
    def setUp(self):
        self.trait = Tuple
