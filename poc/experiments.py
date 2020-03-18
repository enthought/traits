import observe


from traits.api import HasTraits
from trait_types import List


class Foo(HasTraits):

    l = List()


f = Foo(l=[1, 2])

path = observe.ListenerPath(
    node=observe.RequiredTraitListener(name="l", notify=False),
    next=observe.ListenerPath(
        node=observe.ListItemListener(notify=True)
    )
)

def callback(event):
    print("Fire", event.__dict__)

observe.observe(object=f, callback=callback, path=path, remove=False, dispatch="same")

print("Mutate")
f.l.append(1)

print("Reassign")
f.l = []

print("Mutate")
f.l.append(1)