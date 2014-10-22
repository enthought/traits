#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: David C. Morrill
# Description: <Traits component>
#------------------------------------------------------------------------------

from __future__ import absolute_import

from ..api import HasTraits, Property, List, Int, cached_property


class Test(HasTraits):

    __traits__ = {}

    def __value_get(self):
        return self.__dict__.get('_value', 0)

    def __value_set(self, value):
        old_value = self.__dict__.get('_value', 0)
        if value != old_value:
            self._value = value
            self.trait_property_changed('value', old_value, value)

    __traits__['value'] = Property(__value_get, __value_set)


class Test_1 (Test):

    def value_changed(self, value):
        print 'value_changed:', value


class Test_2 (Test):

    def anytrait_changed(self, name, value):
        print 'anytrait_changed for %s: %s' % (name, value)


class Test_3 (Test_2):

    def value_changed(self, value):
        print 'value_changed:', value


def on_value_changed(value):
    print 'on_value_changed:', value


def on_anyvalue_changed(value):
    print 'on_anyvalue_changed:', value


def test_property_notifications():
    Test_1().value = 'test 1'
    Test_2().value = 'test 2'
    Test_3().value = 'test 3'

    test_4 = Test()
    test_4.on_trait_change(on_value_changed, 'value')
    test_4.value = 'test 4'

    test_5 = Test()
    test_5.on_trait_change(on_anyvalue_changed)
    test_5.value = 'test 5'

    test_6 = Test()
    test_6.on_trait_change(on_value_changed, 'value')
    test_6.on_trait_change(on_anyvalue_changed)
    test_6.value = 'test 6'

    test_7 = Test_3()
    test_7.on_trait_change(on_value_changed, 'value')
    test_7.on_trait_change(on_anyvalue_changed)
    test_7.value = 'test 7'


class Entity(HasTraits):
    val = Int

class WrongEntity(HasTraits):
    val2 = Int

class WithList(HasTraits):
    mylist = List
    prop = Property(depends_on='mylist[], mylist.val')

    @cached_property
    def _get_prop(self):
        return sum(i.val for i in self.mylist if isinstance(i, Entity))

def test_property_notification_with_lists():
    v1 = Entity(val=1)
    v2 = Entity(val=2)
    sl = WithList()
    assert sl.prop == 0

    sl.mylist = [v1, v2]
    assert sl.prop == 3

    v3 = WrongEntity(val2=3)  #Entity without proper attribute should not trigger property notification
    sl.mylist.append(v3)
    assert sl.prop == 3

    sl.mylist = [v1,v2, v3, 2] #please do not mind if non-HasTraits object is in list
    assert sl.prop == 3

    sl.mylist.append(v1)
    assert sl.prop == 4
