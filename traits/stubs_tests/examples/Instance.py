# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import typing

from traits.api import HasTraits, Instance


class Fruit:
    info: str

    def __init__(self, info="good for you"):
        self.info = info


class Orange(Fruit):
    pass


class Pizza:
    pass


def fruit_factory(info, other_stuff):
    return Fruit(info=info)


class TestClass(HasTraits):
    itm = Instance(Fruit)
    itm_not_none = Instance(Fruit, allow_none=False)
    itm_allow_none = Instance(Fruit, allow_none=True)
    itm_forward_ref = Instance("Fruit")
    itm_args_kw = Instance(Fruit, ('different info',), {'another_trait': 3})
    itm_args = Instance(Fruit, ('different info',))
    itm_kw = Instance(Fruit, {'info': 'different info'})
    itm_factory = Instance(Fruit, fruit_factory)
    itm_factory_args = Instance(Fruit, fruit_factory, ('different info',))
    itm_factory_args_kw = Instance(
        Fruit,
        fruit_factory,
        ('different info',),
        {'other_stuff': 3},
    )
    itm_factory_kw = Instance(
        Fruit,
        fruit_factory,
        {'other_stuff': 3},
    )


def accepts_fruit(arg: Fruit) -> None:
    pass


def accepts_fruit_or_none(arg: typing.Optional[Fruit]) -> None:
    pass


obj = TestClass()
obj.itm = Orange()
obj.itm = None
obj.itm = Pizza()  # E: assignment
obj.itm_allow_none = Orange()
obj.itm_allow_none = None
obj.itm_allow_none = Pizza()  # E: assignment
obj.itm_not_none = Orange()
obj.itm_not_none = None  # E: assignment
obj.itm_not_none = Pizza()  # E: assignment
obj.itm_forward_ref = Orange()
obj.itm_forward_ref = None


obj = TestClass()
accepts_fruit(obj.itm)  # E: arg-type
accepts_fruit_or_none(obj.itm)
accepts_fruit(obj.itm_allow_none)  # E: arg-type
accepts_fruit_or_none(obj.itm_allow_none)
accepts_fruit(obj.itm_not_none)
accepts_fruit_or_none(obj.itm_not_none)
accepts_fruit(obj.itm_forward_ref)
accepts_fruit_or_none(obj.itm_forward_ref)
