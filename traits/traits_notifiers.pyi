from typing import Callable

_UI_Handler = Callable[..., None] | None


def get_ui_handler() -> _UI_Handler: ...

def set_ui_handler(handler: _UI_Handler) -> None: ...
