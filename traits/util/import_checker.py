import importlib


def import_handler(name):
    """
    Handle import errors

    Parameters
    ----------
    name : Str
        The name of the module being imported, lower case.

    Returns
    -------
    Tuple(Bool, None/module)
        Tuple containing a bool (whether or not a module is available) and the
        module object itself.

    """
    try:
        module = importlib.import_module(name)
        return True, module

    except ImportError:
        return False, None
