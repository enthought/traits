

class CTraitObserverEvent:

    def __init__(self, object, name, old, new):
        self.object = object
        self.name = name
        self.old = old
        self.new = new


class ListObserverEvent:

    def __init__(self, trait_list, trait_list_event):
        self.new = trait_list
        self.added = trait_list_event.added
        self.removed = trait_list_event.removed
        self.index = trait_list_event.index
