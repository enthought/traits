import observe


from traits.api import HasTraits, Int
from trait_types import List


class Bar(HasTraits):

    age = Int()


class Foo(HasTraits):

    l = List(Bar())


def callback(event):
    print("Fire", event.__dict__)


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


print("Mutate list")
f.l.append(Bar())

print("Mutate nested trait on the first item")
f.l[0].age = 10

print("Mutate nested trait on the second item")
f.l[1].age = 10
