import observe


from traits.api import HasTraits, Int
from trait_types import List


class Bar(HasTraits):

    age = Int()


class Foo(HasTraits):

    l = List(Bar())


def callback(event):
    print("**** Fire ****", event.__dict__)


f = Foo(l=[Bar()])
path = observe.ListenerPath(
    node=observe.RequiredTraitListener(name="l", notify=False),
    next=observe.ListenerPath(
        node=observe.ListItemListener(notify=True)
    )
)
observe.observe(object=f, callback=callback, path=path, remove=False, dispatch="same")

path = observe.ListenerPath(
    node=observe.RequiredTraitListener(name="l", notify=False),
    next=observe.ListenerPath(
        node=observe.ListItemListener(notify=True),
        next=observe.ListenerPath(
            node=observe.RequiredTraitListener(name="age", notify=True),
        )
    )
)
observe.observe(object=f, callback=callback, path=path, remove=False, dispatch="same")

print("-----------")
print("Mutate nested trait on the first item")
f.l[0].age = 10

print("-----------")
print("Mutate list")
f.l.append(Bar())

print("-----------")
print("Mutate nested trait on the first item")
f.l[0].age = 20

print("-----------")
print("Mutate nested trait on the second item")
f.l[1].age = 10

print("-----------")
print("Append the same object")
f.l.append(f.l[1])

print("-----------")
print("Mutate the second (and the third) object")
f.l[1].age = 12

print("-----------")
print("Pop the last object, but the same object is still there")
item = f.l.pop()

print("-----------")
print("Mutate the popped item that still lives in the list, which still causes the event to fire")
item.age = 13

print("----------")
print("Pop the last item, now it does not exist in the list")
item = f.l.pop()

print("----------")
print("Mutating this item should not fire")
item.age = 14
