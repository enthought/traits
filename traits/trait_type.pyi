# (C) Copyright 2020-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from typing import Any, Dict, Generic, Optional, Tuple, TypeVar

from .base_trait_handler import BaseTraitHandler as BaseTraitHandler

trait_types: Dict[str, int]

_Accepts = TypeVar('_Accepts')

_Stores = TypeVar('_Stores')


class _TraitMixin(Generic[_Accepts, _Stores]):

    def __call__(self, *args, **kwagrs) -> _TraitMixin: ...

    def __get__(self, object: Any, type: Any) -> _Stores: ...

    def __set__(self, object: Any, value: _Accepts) -> None: ...


class _TraitType(BaseTraitHandler, Generic[_Accepts, _Stores]):
    default_value: _Stores = ...
    metadata: Dict[str, Any] = ...

    def __init__(self, default_value: _Stores = ...,
                 **metadata: Any) -> None: ...

    def init(self) -> None: ...

    def get_default_value(self) -> Tuple[int, _Stores]: ...

    def clone(self, default_value: _Stores = ...,
              **metadata: Any) -> 'TraitType': ...

    def get_value(self, object: Any, name: str,
                  trait: Optional[Any] = ...) -> _Stores: ...

    def set_value(self, object: Any, name: str, value: _Accepts) -> None: ...

    def __call__(self, *args: Any, **kw: Any): ...

    def as_ctrait(self): ...

    @classmethod
    def instantiate_and_get_ctrait(cls): ...

    def __getattr__(self, name: Any): ...

    def __get__(self, object: Any, type: Any) -> _Stores: ...

    def __set__(self, object: Any, value: _Accepts) -> None: ...


TraitType = _TraitType[Any, Any]
