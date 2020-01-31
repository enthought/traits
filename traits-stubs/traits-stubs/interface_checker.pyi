from .has_traits import HasTraits as HasTraits
from typing import Any

logger: Any
BAD_SIGNATURE: str
MISSING_METHOD: str
MISSING_TRAIT: str

class InterfaceError(Exception): ...

class InterfaceChecker(HasTraits):
    def check_implements(self, cls: Any, interfaces: Any, error_mode: Any): ...

checker: Any

def check_implements(cls, interfaces: Any, error_mode: int = ...): ...
