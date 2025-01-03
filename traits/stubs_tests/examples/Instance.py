# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import HasTraits, Instance, Str


class Fruit:
    info = Str("good for you")

    def __init__(self, info="good for you", **traits):
        super().__init__(info=info, **traits)


class Orange(Fruit):
    pass


class Pizza:
    pass


def fruit_factory(info, other_stuff):
    return Fruit(info=info)


class TestClass(HasTraits):
    itm = Instance(Fruit)

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


obj = TestClass()
obj.itm = Orange()
obj.itm = Pizza()
