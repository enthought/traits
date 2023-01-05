# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Test cases for UUID traits. """

import unittest

import uuid

from traits.api import HasTraits, TraitError, UUID


class A(HasTraits):
    id = UUID


class B(HasTraits):
    id = UUID(can_init=True)


class TestUUID(unittest.TestCase):

    def test_bad_assignment(self):
        with self.assertRaises(TraitError):
            a = A()
            a.id = uuid.uuid4()

    def test_bad_init(self):
        with self.assertRaises(TraitError):
            A(id=uuid.uuid4())

    def test_good_init(self):
        B(id=uuid.uuid4())
        B(id=str(uuid.uuid4()))
