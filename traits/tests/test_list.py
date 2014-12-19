#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt

from __future__ import absolute_import

import sys

from traits.testing.unittest_tools import unittest

from ..api import CList, HasTraits, Instance, Int, List, Str, TraitError


class Foo(HasTraits):
    l = List(Str)


class Bar(HasTraits):
    name = Str


class Baz(HasTraits):
    bars = List(Bar)


class BazRef(HasTraits):
    bars = List(Bar, copy='ref')


class DeepBaz(HasTraits):
    baz = Instance(Baz)


class DeepBazBazRef(HasTraits):
    baz = Instance(BazRef)


class CFoo(HasTraits):
    ints = CList(Int)
    strs = CList(Str)


class ListTestCase(unittest.TestCase):

    def test_initialized(self):
        f = Foo()
        self.assertNotEqual(f.l, None)
        self.assertEqual(len(f.l), 0)
        return

    def test_initializer(self):
        f = Foo(l=['a', 'list'])
        self.assertNotEqual(f.l, None)
        self.assertEqual(f.l, ['a', 'list'])
        return

    def test_type_check(self):
        f = Foo()
        f.l.append('string')

        self.assertRaises(TraitError, f.l.append, 123.456)
        return

    def test_append(self):
        f = Foo()
        f.l.append('bar')
        self.assertEqual(f.l, ['bar'])
        return

    def test_remove(self):
        f = Foo()
        f.l.append('bar')
        f.l.remove('bar')
        self.assertEqual(f.l, [])
        return

    def test_slice(self):
        f = Foo(l=['zero', 'one', 'two', 'three'])
        self.assertEqual(f.l[0], 'zero')
        self.assertEqual(f.l[:0], [])
        self.assertEqual(f.l[:1], ['zero'])
        self.assertEqual(f.l[0:1], ['zero'])
        self.assertEqual(f.l[1:], ['one', 'two', 'three'])
        self.assertEqual(f.l[-1], 'three')
        self.assertEqual(f.l[-2], 'two')
        self.assertEqual(f.l[:-1], ['zero', 'one', 'two'])
        return

    def test_retrieve_reference(self):
        f = Foo(l=['initial', 'value'])

        l = f.l
        self.assertIs(l, f.l)

        # no copy on change behavior, l is always a reference
        l.append('change')
        self.assertEqual(f.l, ['initial', 'value', 'change'])

        f.l.append('more change')
        self.assertEqual(l, ['initial', 'value', 'change', 'more change'])
        return

    def test_assignment_makes_copy(self):
        f = Foo(l=['initial', 'value'])
        l = ['new']

        f.l = l
        # same content
        self.assertEqual(l, f.l)

        # different objects
        self.assertIsNot(l, f.l)

        # which means behaviorally...
        l.append('l change')
        self.assertNotIn('l change', f.l)

        f.l.append('f.l change')
        self.assertNotIn('f.l change', l)

        return

    def test_should_not_allow_none(self):
        f = Foo(l=['initial', 'value'])
        try:
            f.l = None
            self.fail('None assigned to List trait.')
        except TraitError:
            pass

    def test_clone(self):
        baz = Baz()
        for name in ['a', 'b', 'c', 'd']:
            baz.bars.append(Bar(name=name))

        # Clone will clone baz, the bars list, and the objects in the list
        baz_copy = baz.clone_traits()

        self.assertIsNot(baz_copy, baz)
        self.assertIsNot(baz_copy.bars, baz.bars)

        self.assertEqual(len(baz_copy.bars), len(baz.bars))
        for bar in baz.bars:
            self.assertNotIn(bar, baz_copy.bars)

        baz_bar_names = [bar.name for bar in baz.bars]
        baz_copy_bar_names = [bar.name for bar in baz_copy.bars]
        baz_bar_names.sort()
        baz_copy_bar_names.sort()
        self.assertEqual(baz_copy_bar_names, baz_bar_names)

        return

    def test_clone_ref(self):
        baz = BazRef()
        for name in ['a', 'b', 'c', 'd']:
            baz.bars.append(Bar(name=name))

        # Clone will clone baz, the bars list, but the objects in the list
        # will not be cloned because the copy metatrait of the List is 'ref'
        baz_copy = baz.clone_traits()

        self.assertIsNot(baz_copy, baz)
        self.assertIsNot(baz_copy.bars, baz.bars)

        self.assertEqual(len(baz_copy.bars), len(baz.bars))
        for bar in baz.bars:
            self.assertIn(bar, baz_copy.bars)

        return

    def test_clone_deep_baz(self):
        baz = Baz()
        for name in ['a', 'b', 'c', 'd']:
            baz.bars.append(Bar(name=name))

        deep_baz = DeepBaz(baz=baz)

        # Clone will clone deep_baz, deep_baz.baz, the bars list,
        # and the objects in the list
        deep_baz_copy = deep_baz.clone_traits()

        self.assertIsNot(deep_baz_copy, deep_baz)
        self.assertIsNot(deep_baz_copy.baz, deep_baz.baz)

        baz_copy = deep_baz_copy.baz

        self.assertIsNot(baz_copy, baz)
        self.assertIsNot(baz_copy.bars, baz.bars)

        self.assertEqual(len(baz_copy.bars), len(baz.bars))
        for bar in baz.bars:
            self.assertNotIn(bar, baz_copy.bars)

        baz_bar_names = [bar.name for bar in baz.bars]
        baz_copy_bar_names = [bar.name for bar in baz_copy.bars]
        baz_bar_names.sort()
        baz_copy_bar_names.sort()
        self.assertEqual(baz_copy_bar_names, baz_bar_names)
        return

    def test_clone_deep_baz_ref(self):
        baz = BazRef()
        for name in ['a', 'b', 'c', 'd']:
            baz.bars.append(Bar(name=name))

        deep_baz = DeepBazBazRef(baz=baz)

        deep_baz_copy = deep_baz.clone_traits()

        self.assertIsNot(deep_baz_copy, deep_baz)
        self.assertIsNot(deep_baz_copy.baz, deep_baz.baz)

        baz_copy = deep_baz_copy.baz

        self.assertIsNot(baz_copy, baz)
        self.assertIsNot(baz_copy.bars, baz.bars)

        self.assertEqual(len(baz_copy.bars), len(baz.bars))
        for bar in baz.bars:
            self.assertIn(bar, baz_copy.bars)
        return

    def test_coercion(self):
        f = CFoo()

        # Test coercion from basic built-in types
        f.ints = [1, 2, 3]
        desired = [1, 2, 3]
        self.assertEqual(f.ints, desired)
        f.ints = (1, 2, 3)
        self.assertEqual(f.ints, desired)

        f.strs = ("abc", "def", "ghi")
        self.assertEqual(f.strs, ["abc", "def", "ghi"])
        f.strs = "abcdef"
        self.assertEqual(f.strs, list("abcdef"))

        try:
            from numpy import array
        except ImportError:
            pass
        else:
            if sys.version_info[0] < 3:
                f.ints = array([1, 2, 3])
                self.assertEqual(f.ints, [1, 2, 3])
            else:
                # These would fail due to np.int_ being an invalid vallue
                # for the Int-trait.
                pass

            f.strs = array(("abc", "def", "ghi"))
            self.assertEqual(f.strs, ["abc", "def", "ghi"])

    def test_extend(self):
        f = Foo()
        f.l = ['4', '5', '6']
        f.l.extend(['1', '2', '3'])
        self.assertEqual(f.l, ['4', '5', '6', '1', '2', '3'])

    def test_iadd(self):
        f = Foo()
        f.l = ['4', '5', '6']
        f.l += ['1', '2', '3']
        self.assertEqual(f.l, ['4', '5', '6', '1', '2', '3'])

    def test_imul(self):
        f = Foo()
        f.l = list('123')
        f.l *= 4
        self.assertEqual(f.l, list('123123123123'))

    def test_sort_no_args(self):
        f = Foo()
        f.l = ["a", "c", "b", "d"]
        f.l.sort()
        self.assertEqual(f.l, ["a", "b", "c", "d"])

    def test_sort_key(self):
        f = Foo()
        f.l = ["a", "c", "b", "d"]
        f.l.sort(key=lambda x: -ord(x))
        self.assertEqual(f.l, ["d", "c", "b", "a"])

    def test_sort_reverse(self):
        f = Foo()
        f.l = ["a", "c", "b", "d"]
        f.l.sort(reverse=True)
        self.assertEqual(f.l, ["d", "c", "b", "a"])

    def test_sort_key_reverse(self):
        f = Foo()
        f.l = ["a", "c", "b", "d"]
        f.l.sort(key=lambda x: -ord(x), reverse=True)
        self.assertEqual(f.l, ["a", "b", "c", "d"])

    @unittest.skipIf(sys.version_info[0] >= 3, "Not for Python 3")
    def test_sort_cmp(self):
        f = Foo()
        f.l = ["a", "c", "b", "d"]
        f.l.sort(cmp=lambda x, y: ord(x) - ord(y))
        self.assertEqual(f.l, ["a", "b", "c", "d"])

    @unittest.skipIf(sys.version_info[0] < 3, "Not for Python 2")
    def test_sort_cmp_error(self):
        f = Foo()
        f.l = ["a", "c", "b", "d"]
        with self.assertRaises(TypeError):
            f.l.sort(cmp=lambda x, y: ord(x) - ord(y))
