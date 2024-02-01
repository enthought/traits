# (C) Copyright 2020-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from typing import Any, Optional

PasswordEditors: Any
MultilineTextEditors: Any
BytesEditors: Any
SourceCodeEditor: Any
HTMLTextEditor: Any
PythonShellEditor: Any
DateEditor: Any
TimeEditor: Any
logger: Any

def password_editor(auto_set: bool = ..., enter_set: bool = ...): ...
def multi_line_text_editor(auto_set: bool = ..., enter_set: bool = ...): ...
def bytes_editor(auto_set: bool = ..., enter_set: bool = ..., encoding: Optional[Any] = ...): ...
def code_editor(): ...
def html_editor(): ...
def shell_editor(): ...
def time_editor(): ...
def date_editor(): ...
def datetime_editor(): ...
def list_editor(trait: Any, handler: Any): ...
