# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import abc
from .adaptation.adaptation_error import AdaptationError as AdaptationError
from .constants import DefaultValue as DefaultValue, TraitKind as TraitKind
from .ctrait import CTrait as CTrait, __newobj__ as __newobj__
from .ctraits import CHasTraits as CHasTraits
from .trait_base import SequenceTypes as SequenceTypes, TraitsCache as TraitsCache, Undefined as Undefined, is_none as is_none, not_event as not_event, not_false as not_false
from .trait_converters import check_trait as check_trait, mapped_trait_for as mapped_trait_for, trait_for as trait_for
from .trait_errors import TraitError as TraitError
from .trait_notifiers import ExtendedTraitChangeNotifyWrapper as ExtendedTraitChangeNotifyWrapper, FastUITraitChangeNotifyWrapper as FastUITraitChangeNotifyWrapper, NewTraitChangeNotifyWrapper as NewTraitChangeNotifyWrapper, StaticAnyTraitChangeNotifyWrapper as StaticAnyTraitChangeNotifyWrapper, StaticTraitChangeNotifyWrapper as StaticTraitChangeNotifyWrapper, TraitChangeNotifyWrapper as TraitChangeNotifyWrapper
from .trait_types import Any as Any, Bool as Bool, Disallow as Disallow, Event as Event, Python as Python
from .traits import ForwardProperty as ForwardProperty, Property as Property, Trait as Trait, generic_trait as generic_trait
from .util.deprecated import deprecated as deprecated
from typing import Optional, Any as _Any

CHECK_INTERFACES: int

class AbstractViewElement(abc.ABC): ...

WrapperTypes: _Any
BoundMethodTypes: _Any
UnboundMethodTypes: _Any
FunctionTypes: _Any
BaseTraits: str
ClassTraits: str
PrefixTraits: str
ListenerTraits: str
ViewTraits: str
InstanceTraits: str
DefaultTraitsView: str
CantHaveDefaultValue: _Any
EmptyList: _Any
DeferredCopy: _Any
extended_trait_pat: _Any
any_trait: _Any

def is_cython_func_or_method(method: _Any): ...
def is_bound_method_type(method: _Any): ...
def is_unbound_method_type(method: _Any): ...
def is_function_type(function: _Any): ...
def get_delegate_pattern(name: _Any, trait: _Any): ...

class _SimpleTest:
    value: _Any = ...
    def __init__(self, value: _Any) -> None: ...
    def __call__(self, test: _Any): ...

class MetaHasTraits(type):
    def __new__(cls, class_name: _Any, bases: _Any, class_dict: _Any): ...
    @classmethod
    def add_listener(cls, listener: _Any, class_name: str = ...) -> None: ...
    @classmethod
    def remove_listener(cls, listener: _Any, class_name: str = ...) -> None: ...

def update_traits_class_dict(class_name: _Any, bases: _Any, class_dict: _Any): ...
def migrate_property(name: _Any, property: _Any, property_info: _Any, class_dict: _Any): ...
def on_trait_change(name: _Any, post_init: bool = ..., dispatch: str = ...): ...
def cached_property(function: _Any): ...
def property_depends_on(dependency: _Any, settable: bool = ..., flushable: bool = ...): ...
def weak_arg(arg: _Any): ...

class HasTraits(CHasTraits, metaclass=MetaHasTraits):
    _traits_cache__: _Any = ...
    wrappers: _Any = ...
    trait_added: _Any = ...
    trait_modified: _Any = ...
    @classmethod
    def add_class_trait(cls, name: _Any, *trait: _Any) -> None: ...
    @classmethod
    def set_trait_dispatch_handler(cls, name: _Any, klass: _Any, override: bool = ...) -> None: ...
    @classmethod
    def trait_subclasses(cls, all: bool = ...): ...
    def has_traits_interface(self, *interfaces: _Any): ...
    def __reduce_ex__(self, protocol: _Any): ...
    def trait_get(self, *names: _Any, **metadata: _Any): ...
    def get(self, *names: _Any, **metadata: _Any): ...
    def trait_set(self, trait_change_notify: bool = ..., **traits: _Any): ...
    def set(self, trait_change_notify: bool = ..., **traits: _Any): ...
    def trait_setq(self, **traits: _Any): ...
    def reset_traits(self, traits: Optional[_Any] = ..., **metadata: _Any): ...
    def copyable_trait_names(self, **metadata: _Any): ...
    def all_trait_names(self): ...
    def __dir__(self): ...
    def copy_traits(self, other: _Any, traits: Optional[_Any] = ..., memo: Optional[_Any] = ..., copy: Optional[_Any] = ..., **metadata: _Any): ...
    def clone_traits(self, traits: Optional[_Any] = ..., memo: Optional[_Any] = ..., copy: Optional[_Any] = ..., **metadata: _Any): ...
    def __deepcopy__(self, memo: _Any): ...
    def edit_traits(self, view: Optional[_Any] = ..., parent: Optional[_Any] = ..., kind: Optional[_Any] = ..., context: Optional[_Any] = ..., handler: Optional[_Any] = ..., id: str = ..., scrollable: Optional[_Any] = ..., **args: _Any): ...
    def trait_context(self): ...
    def trait_view(self, name: Optional[_Any] = ..., view_element: Optional[_Any] = ...): ...
    @classmethod
    def class_trait_view(cls, name: Optional[_Any] = ..., view_element: Optional[_Any] = ...): ...
    def default_traits_view(self): ...
    @classmethod
    def class_default_traits_view(cls): ...
    def trait_views(self, klass: Optional[_Any] = ...): ...
    def trait_view_elements(self): ...
    @classmethod
    def class_trait_view_elements(cls): ...
    def configure_traits(self, filename: Optional[_Any] = ..., view: Optional[_Any] = ..., kind: Optional[str] = ..., edit: bool = ..., context: Optional[_Any] = ..., handler: Optional[_Any] = ..., id: str = ..., scrollable: Optional[_Any] = ..., **args: _Any): ...
    def editable_traits(self): ...
    @classmethod
    def class_editable_traits(cls): ...
    def visible_traits(self): ...
    @classmethod
    def class_visible_traits(cls): ...
    def print_traits(self, show_help: bool = ..., **metadata: _Any) -> None: ...
    def on_trait_change(self, handler: _Any, name: Optional[_Any] = ..., remove: bool = ..., dispatch: str = ..., priority: bool = ..., deferred: bool = ..., target: Optional[_Any] = ...) -> None: ...
    on_trait_event: _Any = ...
    def sync_trait(self, trait_name: _Any, object: _Any, alias: Optional[_Any] = ..., mutual: bool = ..., remove: bool = ...): ...
    def add_trait(self, name: _Any, *trait: _Any) -> None: ...
    def remove_trait(self, name: _Any): ...
    def trait(self, name: str, force: bool = ..., copy: bool = ...): ...
    def base_trait(self, name: _Any): ...
    def validate_trait(self, name: _Any, value: _Any): ...
    def traits(self, **metadata: _Any): ...
    @classmethod
    def class_traits(cls, **metadata: _Any): ...
    def trait_names(self, **metadata: _Any): ...
    @classmethod
    def class_trait_names(cls, **metadata: _Any): ...
    def __prefix_trait__(self, name: _Any, is_set: _Any): ...
    def add_trait_listener(self, object: _Any, prefix: str = ...) -> None: ...
    def remove_trait_listener(self, object: _Any, prefix: str = ...) -> None: ...

class HasStrictTraits(HasTraits): ...

class HasRequiredTraits(HasStrictTraits):
    def __init__(self, **traits: _Any) -> None: ...

class HasPrivateTraits(HasTraits):
    __: _Any = ...

class ABCMetaHasTraits(abc.ABCMeta, MetaHasTraits): ...
class ABCHasTraits(HasTraits, metaclass=ABCMetaHasTraits): ...
class ABCHasStrictTraits(ABCHasTraits): ...

class SingletonHasTraits(HasTraits):
    def __new__(cls, *args: _Any, **traits: _Any): ...

class SingletonHasStrictTraits(HasStrictTraits):
    def __new__(cls, *args: _Any, **traits: _Any): ...

class SingletonHasPrivateTraits(HasPrivateTraits):
    def __new__(cls, *args: _Any, **traits: _Any): ...

class Vetoable(HasStrictTraits):
    veto: _Any = ...

VetoableEvent: _Any

class MetaInterface(ABCMetaHasTraits):
    def __call__(self, adaptee: _Any, default: _Any = ...): ...

class Interface(HasTraits, metaclass=MetaInterface): ...

def provides(*protocols: _Any): ...
def isinterface(klass: _Any): ...

class ISerializable(Interface): ...

class traits_super(super):
    def __getattribute__(self, name: _Any): ...
