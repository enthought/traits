

class CTraitObserverEvent:
    """ Event object to represent change on a trait."""

    def __init__(self, object, name, old, new):
        """
        Parameters
        ----------
        object : HasTraits
            Object on which the trait is defined.
        name : str
            Name of the trait.
        old : any
            Previous value of the trait
        new : any
            New value of the trait
        """
        self.object = object
        self.name = name
        self.old = old
        self.new = new


class ListObserverEvent:
    """ Event object to represent mutation on a list.

    Attributes
    ----------
    new : list
        The list being mutated, with the new content.
    index : int or slice
        The index used for the mutation.
    added : list
        Values added to the list.
    removed : list
        Values removed from the list.
    """

    def __init__(self, trait_list, index, removed, added):
        self.new = trait_list
        self.added = added
        self.removed = removed
        self.index = index


class DictItemObserverEvent:
    """ Event object to represent changes on dict items.
    """

    def __init__(self, trait_dict, trait_dict_event):
        self.new = trait_dict
        self.added = trait_dict_event.added
        self.changed = trait_dict_event.changed
        self.removed = trait_dict_event.removed
