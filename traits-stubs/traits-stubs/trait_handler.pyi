from .base_trait_handler import BaseTraitHandler as BaseTraitHandler
from .trait_base import class_of as class_of
from .trait_errors import TraitError as TraitError
from typing import Any

class TraitHandler(BaseTraitHandler):
    def validate(self, object: Any, name: Any, value: Any) -> None: ...
