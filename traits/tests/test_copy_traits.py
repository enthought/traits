# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.api import HasTraits, Instance, Str


class Shared(HasTraits):
    s = Str("new instance of Shared")


class Foo(HasTraits):
    s = Str("new instance of Foo")
    shared = Instance(Shared)


class Bar(HasTraits):
    s = Str("new instance of Bar")
    foo = Instance(Foo)
    shared = Instance(Shared)


class Baz(HasTraits):
    s = Str("new instance of Baz")
    bar = Instance(Bar)
    shared = Instance(Shared)


class CopyTraitsBase(unittest.TestCase):
    """ Validate that copy_traits
    """

    __test__ = False

    def setUp(self):
        super().setUp()
        self.shared = Shared(s="shared")
        self.foo = Foo(shared=self.shared, s="foo")
        self.bar = Bar(shared=self.shared, foo=self.foo, s="bar")
        self.baz = Baz(shared=self.shared, bar=self.bar, s="baz")

        self.shared2 = Shared(s="shared2")
        self.foo2 = Foo(shared=self.shared2, s="foo2")
        self.bar2 = Bar(shared=self.shared2, foo=self.foo2, s="bar2")
        self.baz2 = Baz(shared=self.shared2, bar=self.bar2, s="baz2")

    def set_shared_copy(self, value):
        """ Change the copy style for the 'shared' traits. """
        self.foo.base_trait("shared").copy = value
        self.bar.base_trait("shared").copy = value
        self.baz.base_trait("shared").copy = value


class TestCopyTraitsSetup(CopyTraitsBase):
    __test__ = True

    def setUp(self):
        super().setUp()

    def test_setup(self):
        self.assertIs(self.foo, self.bar.foo)
        self.assertIs(self.bar, self.baz.bar)
        self.assertIs(self.foo.shared, self.shared)
        self.assertIs(self.bar.shared, self.shared)
        self.assertIs(self.baz.shared, self.shared)

        self.assertIs(self.foo2, self.bar2.foo)
        self.assertIs(self.bar2, self.baz2.bar)
        self.assertIs(self.foo2.shared, self.shared2)
        self.assertIs(self.bar2.shared, self.shared2)
        self.assertIs(self.baz2.shared, self.shared2)


class CopyTraits(object):
    def test_baz2_s(self):
        self.assertEqual(self.baz2.s, "baz")
        self.assertEqual(self.baz2.s, self.baz.s)

    def test_baz2_bar_s(self):
        self.assertEqual(self.baz2.bar.s, "bar")
        self.assertEqual(self.baz2.bar.s, self.baz.bar.s)

    def test_baz2_bar_foo_s(self):
        self.assertEqual(self.baz2.bar.foo.s, "foo")
        self.assertEqual(self.baz2.bar.foo.s, self.baz.bar.foo.s)

    def test_baz2_shared_s(self):
        self.assertEqual(self.baz2.shared.s, "shared")
        self.assertEqual(self.baz2.bar.shared.s, "shared")
        self.assertEqual(self.baz2.bar.foo.shared.s, "shared")

    def test_baz2_bar(self):
        # First hand Instance trait is different and
        # is not the same object as the source.

        self.assertIsNot(self.baz2.bar, None)
        self.assertIsNot(self.baz2.bar, self.bar2)
        self.assertIsNot(self.baz2.bar, self.baz.bar)

    def test_baz2_bar_foo(self):
        # Second hand Instance trait is a different object and
        # is not the same object as the source.

        self.assertIsNot(self.baz2.bar.foo, None)
        self.assertIsNot(self.baz2.bar.foo, self.foo2)
        self.assertIsNot(self.baz2.bar.foo, self.baz.bar.foo)


class CopyTraitsSharedCopyNone(object):
    def test_baz2_shared(self):
        # First hand Instance trait is a different object and
        # is not the same object as the source.

        self.assertIsNot(self.baz2.shared, None)
        self.assertIsNot(self.baz2.shared, self.shared2)
        self.assertIsNot(self.baz2.shared, self.shared)

    def test_baz2_bar_shared(self):
        # Second hand Instance that was shared is a different object and
        # not the same object as the source and
        # not the same object as the new first hand instance that was the same.
        # I.e. There are now (at least) two copies of one original object.

        self.assertIsNot(self.baz2.bar.shared, None)
        self.assertIsNot(self.baz2.bar.shared, self.shared2)
        self.assertIsNot(self.baz2.bar.shared, self.shared)
        self.assertIsNot(self.baz2.bar.shared, self.baz2.shared)

    def test_baz2_bar_foo_shared(self):
        # Third hand Instance that was shared is a different object and
        # not the same object as the source and
        # not the same object as the new first hand instance that was the same.
        # I.e. There are now (at least) two copies of one original object.

        self.assertIsNot(self.baz2.bar.foo.shared, None)
        self.assertIsNot(self.baz2.bar.foo.shared, self.shared2)
        self.assertIsNot(self.baz2.bar.foo.shared, self.shared)
        self.assertIsNot(self.baz2.bar.foo.shared, self.baz2.shared)

    def test_baz2_bar_and_foo_shared(self):
        #
        # THE BEHAVIOR DEMONSTRATED BY THIS TEST CASE DOES NOT SEEM TO BE
        # CORRECT.
        #
        # Second and Third hand Instance object that was shared with first hand
        # instance are the same as each other but
        # Every reference to the same original object has been replace by
        # a reference to the same copy of the same source object except the
        # first hand reference which is a different copy.
        # I.e. The shared relationship has been fubarred by copy_traits: it's
        # not maintained, but not completely destroyed.
        self.assertIs(self.baz2.bar.shared, self.baz2.bar.foo.shared)
        self.assertIsNot(self.baz2.shared, self.baz2.bar.foo.shared)


class TestCopyTraitsSharedCopyNone(CopyTraits, CopyTraitsSharedCopyNone):
    __test__ = False

    def setUp(self):
        # deep is the default value for Instance trait copy
        self.set_shared_copy("deep")


class TestCopyTraitsCopyNotSpecified(
    CopyTraitsBase, TestCopyTraitsSharedCopyNone
):
    __test__ = True

    def setUp(self):
        CopyTraitsBase.setUp(self)
        TestCopyTraitsSharedCopyNone.setUp(self)
        self.baz2.copy_traits(self.baz)


class TestCopyTraitsCopyShallow(CopyTraitsBase, TestCopyTraitsSharedCopyNone):
    __test__ = True

    def setUp(self):
        CopyTraitsBase.setUp(self)
        TestCopyTraitsSharedCopyNone.setUp(self)
        self.baz2.copy_traits(self.baz, copy="shallow")


class TestCopyTraitsCopyDeep(CopyTraitsBase, TestCopyTraitsSharedCopyNone):
    __test__ = True

    def setUp(self):
        CopyTraitsBase.setUp(self)
        TestCopyTraitsSharedCopyNone.setUp(self)
        self.baz2.copy_traits(self.baz, copy="deep")


class CopyTraitsSharedCopyRef(object):
    def test_baz2_shared(self):
        # First hand Instance trait is a different object and
        # is the same object as the source.

        self.assertIsNot(self.baz2.shared, None)
        self.assertIsNot(self.baz2.shared, self.shared2)
        self.assertIs(self.baz2.shared, self.shared)

    def test_baz2_bar_shared(self):
        self.assertIsNot(self.baz2.bar.shared, None)
        self.assertIsNot(self.baz2.bar.shared, self.shared2)
        self.assertIs(self.baz2.bar.shared, self.shared)
        self.assertIs(self.baz2.bar.shared, self.baz2.shared)

    def test_baz2_bar_foo_shared(self):
        self.assertIsNot(self.baz2.bar.foo.shared, None)
        self.assertIsNot(self.baz2.bar.foo.shared, self.shared2)
        self.assertIs(self.baz2.bar.foo.shared, self.shared)
        self.assertIs(self.baz2.bar.foo.shared, self.baz2.shared)

    def test_baz2_bar_and_foo_shared(self):
        self.assertIs(self.baz2.bar.shared, self.baz2.bar.foo.shared)
        self.assertIs(self.baz2.shared, self.baz2.bar.foo.shared)


class TestCopyTraitsSharedCopyRef(CopyTraits, CopyTraitsSharedCopyRef):
    __test__ = False

    def setUp(self):
        self.set_shared_copy("ref")


# The next three tests demonstrate that a 'ref' trait is always copied as a
# reference regardless of the copy argument to copy_traits.  That is, shallow
# and deep are indistinguishable.
class TestCopyTraitsCopyNotSpecifiedSharedRef(
    CopyTraitsBase, TestCopyTraitsSharedCopyRef
):
    __test__ = True

    def setUp(self):
        CopyTraitsBase.setUp(self)
        TestCopyTraitsSharedCopyRef.setUp(self)
        self.baz2.copy_traits(self.baz)


class TestCopyTraitsCopyShallowSharedRef(
    CopyTraitsBase, TestCopyTraitsSharedCopyRef
):
    __test__ = True

    def setUp(self):
        CopyTraitsBase.setUp(self)
        TestCopyTraitsSharedCopyRef.setUp(self)
        self.baz2.copy_traits(self.baz, copy="shallow")


class TestCopyTraitsCopyDeepSharedRef(
    CopyTraitsBase, TestCopyTraitsSharedCopyRef
):
    __test__ = True

    def setUp(self):
        CopyTraitsBase.setUp(self)
        TestCopyTraitsSharedCopyRef.setUp(self)
        self.baz2.copy_traits(self.baz, copy="deep")
