import contextlib
from unittest import mock

import observe

from traits.api import HasTraits, Int
from trait_types import List

CALL = mock.MagicMock()


@contextlib.contextmanager
def check_call_count(expected):
    CALL.reset_mock()
    try:
        yield
    finally:
        assert CALL.call_count == expected


class Bar(HasTraits):

    age = Int()


class Foo(HasTraits):

    l = List(Bar())


def callback(event):
    print("**** Fire ****", event.__dict__)
    CALL()


f = Foo(l=[Bar()])
item_path = observe.ListenerPath(
    node=observe.RequiredTraitListener(name="l", notify=False),
    next=observe.ListenerPath(
        node=observe.ListItemListener(notify=True)
    )
)
observe.observe(object=f, callback=callback, path=item_path, remove=False, dispatch="same")

age_path = observe.ListenerPath(
    node=observe.RequiredTraitListener(name="l", notify=False),
    next=observe.ListenerPath(
        node=observe.ListItemListener(notify=True),
        next=observe.ListenerPath(
            node=observe.RequiredTraitListener(name="age", notify=True),
        )
    )
)
observe.observe(object=f, callback=callback, path=age_path, remove=False, dispatch="same")


print("-----------")
print("Mutate nested trait on the first item")
with check_call_count(1):
    f.l[0].age = 10

print("-----------")
print("Mutate list")
with check_call_count(1):
    f.l.append(Bar())

print("-----------")
print("Mutate nested trait on the first item")
with check_call_count(1):
    f.l[0].age = 20

print("-----------")
print("Mutate nested trait on the second item")
with check_call_count(1):
    f.l[1].age = 10

print("-----------")
print("Append the same object")
with check_call_count(1):
    f.l.append(f.l[1])

print("-----------")
print("Mutate the second object (same object as the third)")
with check_call_count(1):
    f.l[1].age = 12

print("-----------")
print("Pop the last object, but the same object is still there")
with check_call_count(1):
    item = f.l.pop()

print("-----------")
print("Mutate the popped item that still lives in the list, which still causes the event to fire")
with check_call_count(1):
    item.age = 13

print("----------")
print("Pop the last item, now it does not exist in the list")
with check_call_count(1):
    item = f.l.pop()

print("----------")
print("Mutating this item should not fire")
with check_call_count(0):
    item.age = 14


print("----------")
print("Two lists sharing the same object")
f1 = Foo()
f2 = Foo()
bar = Bar()
f1.l = [bar]
f2.l = [bar]
age_path2 = observe.ListenerPath(
    node=observe.RequiredTraitListener(name="l", notify=False),
    next=observe.ListenerPath(
        node=observe.ListItemListener(notify=False),
        next=observe.ListenerPath(
            node=observe.RequiredTraitListener(name="age", notify=True),
        )
    )
)
observe.observe(object=f1, callback=callback, path=age_path, remove=False, dispatch="same")
observe.observe(object=f2, callback=callback, path=age_path, remove=False, dispatch="same")
print("Mutating the object")
print("Should we fire once, or twice?")
with check_call_count(1):
    bar.age = 12
