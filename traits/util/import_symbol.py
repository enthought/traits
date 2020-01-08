""" A function to import symbols. """

from importlib import import_module

from traits.trait_base import xgetattr


def import_symbol(symbol_path):
    """ Import the symbol defined by the specified symbol path.

    Examples
    --------

    import_symbol('tarfile:TarFile') -> TarFile
    import_symbol('tarfile:TarFile.open') -> TarFile.open

    To allow compatibility with old-school traits symbol names we also allow
    all-dotted paths, but in this case you can only import top-level names
    from the module.

    import_symbol('tarfile.TarFile') -> TarFile

    """

    if ":" in symbol_path:
        module_name, symbol_name = symbol_path.split(":")

        module = import_module(module_name)
        symbol = xgetattr(module, symbol_name)

    else:
        components = symbol_path.split(".")
        module_name = ".".join(components[:-1])
        symbol_name = components[-1]

        module = import_module(module_name)
        symbol = getattr(module, symbol_name)

    return symbol
