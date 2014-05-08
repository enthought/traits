# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: David C. Morrill Date: 10/22/2003 Description: Unit test case for
# Traits event notification handling.

from __future__ import absolute_import

import unittest

from ..api import HasTraits


class TestBase(HasTraits):
    __traits__ = {
        't1': 0,
        't2': 0
    }

    def __init__(self, **traits):
        HasTraits.__init__(self, **traits)
        self.events = []

    def test(self):
        self.t1 = 1
        self.t2 = 2


class Test1(TestBase):

    def t1_changed(self, old, new):
        self.events.append(('t1 changed:', old, new))

    def t2_changed(self, old, new):
        self.events.append(('t2 changed:', old, new))


class Test2(Test1):

    def anytrait_changed(self, name, old, new):
        self.events.append(('anytrait changed:', name, old, new))


class Test3(TestBase):

    def anytrait_changed(self, name, old, new):
        self.events.append(('anytrait changed:', name, old, new))


class Test4(TestBase):

    def __init__(self, **traits):
        TestBase.__init__(self, **traits)
        self.on_trait_change(self.on_anytrait)

    def on_anytrait(self, object, name, old, new):
        self.events.append(('on anytrait changed:', name, old, new))


class Test5(TestBase):

    def __init__(self, **traits):
        TestBase.__init__(self, **traits)
        self.on_trait_change(self.t1_trait, 't1')
        self.on_trait_change(self.t2_trait, 't2')

    def t1_trait(self, object, name, old, new):
        self.events.append(('on t1 changed:', old, new))

    def t2_trait(self, object, name, old, new):
        self.events.append(('on t2 changed:', old, new))


class Test6(Test5):

    def __init__(self, **traits):
        Test5.__init__(self, **traits)
        self.on_trait_change(self.on_anytrait)

    def on_anytrait(self, object, name, old, new):
        self.events.append(('on anytrait changed:', name, old, new))


class Test7(Test1):

    def __init__(self, **traits):
        Test1.__init__(self, **traits)
        self.on_trait_change(self.t1_trait, 't1')
        self.on_trait_change(self.t2_trait, 't2')

    def t1_trait(self, object, name, old, new):
        self.events.append(('on t1 changed:', old, new))

    def t2_trait(self, object, name, old, new):
        self.events.append(('on t2 changed:', old, new))


class Test8(Test2):

    def __init__(self, **traits):
        Test2.__init__(self, **traits)
        self.on_trait_change(self.t1_trait, 't1')
        self.on_trait_change(self.t2_trait, 't2')
        self.on_trait_change(self.on_anytrait)

    def on_anytrait(self, object, name, old, new):
        self.events.append(('on anytrait changed:', name, old, new))

    def t1_trait(self, object, name, old, new):
        self.events.append(('on t1 changed:', old, new))

    def t2_trait(self, object, name, old, new):
        self.events.append(('on t2 changed:', old, new))


class TestEvents(unittest.TestCase):
    def test_events_1(self):
        test = Test1()
        test.test()
        self.assertEqual(test.events, [])

    def test_events_2(self):
        test = Test2()
        test.test()
        self.assertEqual(test.events, [])

    def test_events_3(self):
        test = Test3()
        test.test()
        self.assertEqual(test.events, [])

    def test_events_4(self):
        test = Test4()
        test.test()
        events = test.events
        self.assertEqual(len(events), 2)
        for event in events:
            self.assertEqual(event[0], 'on anytrait changed:')
            self.assertEqual(event[1], 'trait_added')

        # Compare sets to avoid making any assumptions about event ordering.
        new_values = set([event[3] for event in events])
        self.assertEqual(new_values, set(['t1', 't2']))

    def test_events_5(self):
        test = Test5()
        test.test()
        self.assertEqual(test.events, [])

    def test_events_6(self):
        test = Test6()
        test.test()
        self.assertEqual(test.events, [])

    def test_events_7(self):
        test = Test7()
        self.assertEqual(test.events, [])
        test.test()

    def test_events_8(self):
        test = Test8()
        self.assertEqual(test.events, [])
        test.test()


if __name__ == '__main__':
    unittest.main()
