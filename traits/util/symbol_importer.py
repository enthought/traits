""" The default import manager implementation. """


from traits.has_traits import HasTraits


class SymbolImporter(HasTraits):
    """ The default import manager implementation.

    It's just a guess, but I think using an import manager to do all imports
    will make debugging easier (as opposed to just letting imports happen from
    all over the place).

    """

    ###########################################################################
    # 'SymbolImporter' interface.
    ###########################################################################

    def import_symbol(self, symbol_path):
        """ Import the symbol defined by the specified symbol path. """

        if ':' in symbol_path:
            module_name, symbol_name = symbol_path.split(':')

            module = self._import_module(module_name)
            symbol = eval(symbol_name, module.__dict__)

        else:
            components = symbol_path.split('.')

            module_name = '.'.join(components[:-1])
            symbol_name = components[-1]

            module = __import__(
                module_name, globals(), locals(), [symbol_name]
            )

            symbol = getattr(module, symbol_name)

        return symbol

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _import_module(self, module_name):
        """ Import the module with the specified (and possibly dotted) name.

        Returns the imported module.

        This method is copied from the documentation of the '__import__'
        function in the Python Library Reference Manual.

        """

        module = __import__(module_name)

        components = module_name.split('.')
        for component in components[1:]:
            module = getattr(module, component)

        return module


#: Global import manager, for convenience.
symbol_importer = SymbolImporter()

import_symbol = symbol_importer.import_symbol

#### EOF ######################################################################
