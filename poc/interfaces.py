import abc


class INotifiableObject(abc.ABC):

    @abc.abstractmethod
    def _notifiers(self, force_create):
        return []
