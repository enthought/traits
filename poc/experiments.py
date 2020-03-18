import observe


from traits.api import HasTraits
from trait_types import List


class Foo(HasTraits):

    l = List()


f = Foo(l=[1, 2])
print(type(f.l))

path = observe.ListenerPath(
    node=observe.RequiredTraitListener(name="l", notify=True),
    next=observe.ListenerPath(
        node=observe.ListItemListener(notify=True)
    )
)

def callback(event):
    print(event)
    print("HERE")

observe.observe(object=f, callback=callback, path=path, remove=False, dispatch="same")

f.l = []
f.l.append(1)