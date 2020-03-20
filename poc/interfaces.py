import abc


class INotifiableObject(abc.ABC):

    @abc.abstractmethod
    def _notifiers(self, force_create):
        return []


class INotifier(abc.ABC):

    # FIXME: observer should be renamed to callback!
    def __init__(self, observer, owner, target, event_factory):
        pass

    def increment_target_count(target):
        pass

    def decrement_target_count(target):
        pass
