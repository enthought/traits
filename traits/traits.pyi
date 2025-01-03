# (C) Copyright 2020-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from typing import (
    Any as _Any,
    Optional,
    Callable as _CallableType,
    Dict as _DictType,
)

NoneType: _Any
ConstantTypes: _Any
PythonTypes: _Any
CallableTypes: _Any
TraitTypes: _Any
DefaultValues: _Any


class _InstanceArgs:
    def __init__(self, factory: _Any, args: _Any, kw: _Any) -> None: ...


class Default:
    default_value: _Any = ...

    def __init__(self, func: Optional[_Any] = ..., args: _Any = ...,
                 kw: Optional[_Any] = ...) -> None: ...


def Trait(*value_type: _Any,
          **metadata: _DictType[str, _Any]): ...


def Property(fget: Optional[_CallableType] = ...,
             fset: Optional[_CallableType] = ...,
             fvalidate: Optional[_CallableType] = ...,
             force: bool = ...,
             handler: Optional[_CallableType] = ...,
             trait: Optional[_Any] = ...,
             **metadata: _Any) -> _Any:
    ...


class ForwardProperty:
    metadata: _Any = ...
    validate: _Any = ...
    handler: _Any = ...

    def __init__(self, metadata: _Any,
                 validate: Optional[_Any] = ...,
                 handler: Optional[_Any] = ...) -> None: ...


generic_trait: _Any
