# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import datetime
from functools import partial
import logging

# -------------------------------------------------------------------------------
#  Editor factory functions:
# -------------------------------------------------------------------------------

PasswordEditors = {}
MultilineTextEditors = {}
BytesEditors = {}
SourceCodeEditor = None
HTMLTextEditor = None
PythonShellEditor = None
DateEditor = None
TimeEditor = None

# -------------------------------------------------------------------------------
#  Logging:
# -------------------------------------------------------------------------------

logger = logging.getLogger(__name__)


def password_editor(auto_set=True, enter_set=False):
    """ Factory function that returns an editor for passwords.
    """
    if (auto_set, enter_set) not in PasswordEditors:
        from traitsui.api import TextEditor

        PasswordEditors[auto_set, enter_set] = TextEditor(
            password=True, auto_set=auto_set, enter_set=enter_set
        )

    return PasswordEditors[auto_set, enter_set]


def multi_line_text_editor(auto_set=True, enter_set=False):
    """ Factory function that returns a text editor for multi-line strings.
    """
    if (auto_set, enter_set) not in MultilineTextEditors:
        from traitsui.api import TextEditor

        MultilineTextEditors[auto_set, enter_set] = TextEditor(
            multi_line=True, auto_set=auto_set, enter_set=enter_set
        )

    return MultilineTextEditors[auto_set, enter_set]


def bytes_editor(auto_set=True, enter_set=False, encoding=None):
    """ Factory function that returns a text editor for bytes.
    """
    if (auto_set, enter_set, encoding) not in BytesEditors:
        from traitsui.api import TextEditor

        if encoding is None:
            format = bytes.hex
            evaluate = bytes.fromhex
        else:
            format = partial(bytes.decode, encoding=encoding)
            evaluate = partial(str.encode, encoding=encoding)

        BytesEditors[(auto_set, enter_set, encoding)] = TextEditor(
            multi_line=True,
            format_func=format,
            evaluate=evaluate,
            auto_set=auto_set,
            enter_set=enter_set,
        )

    return BytesEditors[(auto_set, enter_set, encoding)]


def code_editor():
    """ Factory function that returns an editor that treats a multi-line string
    as source code.
    """
    global SourceCodeEditor

    if SourceCodeEditor is None:
        from traitsui.api import CodeEditor

        SourceCodeEditor = CodeEditor()

    return SourceCodeEditor


def html_editor():
    """ Factory function for an "editor" that displays a multi-line string as
    interpreted HTML.
    """
    global HTMLTextEditor

    if HTMLTextEditor is None:
        from traitsui.api import HTMLEditor

        HTMLTextEditor = HTMLEditor()

    return HTMLTextEditor


def shell_editor():
    """ Factory function that returns a Python shell for editing Python values.
    """
    global PythonShellEditor

    if PythonShellEditor is None:
        from traitsui.api import ShellEditor

        PythonShellEditor = ShellEditor()

    return PythonShellEditor


def time_editor():
    """ Factory function that returns a Time editor for editing Time values.
    """
    global TimeEditor

    if TimeEditor is None:
        from traitsui.api import TimeEditor

        TimeEditor = TimeEditor()

    return TimeEditor


def date_editor():
    """ Factory function that returns a Date editor for editing Date values.
    """
    global DateEditor

    if DateEditor is None:
        from traitsui.api import DateEditor

        DateEditor = DateEditor()

    return DateEditor


def _datetime_str_to_datetime(datetime_str, format="%Y-%m-%dT%H:%M:%S"):
    """ Returns the datetime object for a datetime string in the specified
    format (default ISO format).

    Raises a ValueError if datetime_str does not match the format.
    """
    if datetime_str is not None:
        return datetime.datetime.strptime(datetime_str, format)


def _datetime_to_datetime_str(datetime_obj, format="%Y-%m-%dT%H:%M:%S"):
    """ Returns a string representation for a datetime object in the specified
    format (default ISO format).
    """
    if datetime_obj is not None:
        return datetime.date.strftime(datetime_obj, format)


def datetime_editor():
    """ Factory function that returns an editor with date & time for
    editing Datetime values.
    """

    try:
        from traitsui.api import DatetimeEditor

        return DatetimeEditor()

    except ImportError:

        logger.warn(msg="Could not import DatetimeEditor from "
                        "traitsui.api, using TextEditor instead")

        from traitsui.api import TextEditor

        return TextEditor(
            evaluate=_datetime_str_to_datetime,
            format_func=_datetime_to_datetime_str
        )


def _expects_hastraits_instance(handler):
    """ Does a trait handler or type expect a HasTraits subclass instance?
    """
    from traits.api import HasTraits, BaseInstance, TraitInstance

    if isinstance(handler, TraitInstance):
        cls = handler.aClass
    elif isinstance(handler, BaseInstance):
        cls = handler.klass
    else:
        return False
    return issubclass(cls, HasTraits)


def _instance_handler_factory(handler):
    """ Get the instance factory of an Instance or TraitInstance
    """
    from traits.api import BaseInstance, TraitInstance

    if isinstance(handler, TraitInstance):
        return handler.aClass
    elif isinstance(handler, BaseInstance):
        return handler.default_value
    else:
        msg = "handler should be TraitInstance or BaseInstance, but got {}"
        raise ValueError(msg.format(repr(handler)))


def list_editor(trait, handler):
    """ Factory that constructs an appropriate editor for a list.
    """
    item_handler = handler.item_trait.handler
    if _expects_hastraits_instance(item_handler):
        from traitsui.table_filter import (
            EvalFilterTemplate,
            RuleFilterTemplate,
            MenuFilterTemplate,
            EvalTableFilter,
        )
        from traitsui.api import TableEditor

        return TableEditor(
            filters=[
                RuleFilterTemplate,
                MenuFilterTemplate,
                EvalFilterTemplate,
            ],
            edit_view="",
            orientation="vertical",
            search=EvalTableFilter(),
            deletable=True,
            show_toolbar=True,
            reorderable=True,
            row_factory=_instance_handler_factory(item_handler),
        )
    else:
        from traitsui.api import ListEditor

        return ListEditor(
            trait_handler=handler,
            rows=trait.rows if trait.rows else 5,
            use_notebook=bool(trait.use_notebook),
            page_name=trait.page_name if trait.page_name else "",
        )
