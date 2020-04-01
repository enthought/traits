

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

    def __init__(self, trait_list, trait_list_event):
        self.new = trait_list
        self.added = trait_list_event.added
        self.removed = trait_list_event.removed
        self.index = trait_list_event.index
