# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Editor factory functions.
"""

import datetime
from functools import partial
import logging


logger = logging.getLogger(__name__)


def password_editor(auto_set=True, enter_set=False):
    """ Factory function that returns an editor for passwords.
    """
    from traitsui.api import TextEditor
    return TextEditor(
        password=True, auto_set=auto_set, enter_set=enter_set
    )


def multi_line_text_editor(auto_set=True, enter_set=False):
    """ Factory function that returns a text editor for multi-line strings.
    """
    from traitsui.api import TextEditor
    return TextEditor(
        multi_line=True, auto_set=auto_set, enter_set=enter_set
    )


def bytes_editor(auto_set=True, enter_set=False, encoding=None):
    """ Factory function that returns a text editor for bytes.
    """
    from traitsui.api import TextEditor

    if encoding is None:
        format = bytes.hex
        evaluate = bytes.fromhex
    else:
        format = partial(bytes.decode, encoding=encoding)
        evaluate = partial(str.encode, encoding=encoding)

    return TextEditor(
        multi_line=True,
        format_func=format,
        evaluate=evaluate,
        auto_set=auto_set,
        enter_set=enter_set,
    )


def code_editor():
    """ Factory function that returns an editor that treats a multi-line string
    as source code.
    """
    from traitsui.api import CodeEditor
    return CodeEditor()


def html_editor():
    """ Factory function for an "editor" that displays a multi-line string as
    interpreted HTML.
    """
    from traitsui.api import HTMLEditor
    return HTMLEditor()


def shell_editor():
    """ Factory function that returns a Python shell for editing Python values.
    """
    from traitsui.api import ShellEditor
    return ShellEditor()


def time_editor():
    """ Factory function that returns a Time editor for editing Time values.
    """
    from traitsui.api import TimeEditor
    return TimeEditor()


def date_editor():
    """ Factory function that returns a Date editor for editing Date values.
    """
    from traitsui.api import DateEditor
    return DateEditor()


def _datetime_str_to_datetime(datetime_str, format="%Y-%m-%dT%H:%M:%S"):
    """ Returns the datetime object for a datetime string in the specified
    format (default ISO format).

    Raises a ValueError if datetime_str does not match the format.
    """
    # Allow the empty string to be translated to None.
    if not datetime_str:
        return None
    return datetime.datetime.strptime(datetime_str, format)


def _datetime_to_datetime_str(datetime_obj, format="%Y-%m-%dT%H:%M:%S"):
    """ Returns a string representation for a datetime object in the specified
    format (default ISO format).
    """
    # A Datetime trait can contain None. We translate that to an empty string.
    if datetime_obj is None:
        return ""
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
