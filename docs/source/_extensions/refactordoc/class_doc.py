# -*- coding: UTF-8 -*-
#------------------------------------------------------------------------------
#  file: class_doc.py
#  License: LICENSE.TXT
#
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from base_doc import BaseDoc
from line_functions import get_indent, replace_at, add_indent
from definition_items import (MethodItem, AttributeItem, TableLineItem,
                              max_attribute_length, max_attribute_index,
                              ListItem)


class ClassDoc(BaseDoc):
    """ Docstring refactoring for classes.

    The class provides the following refactoring methods.

    Methods
    -------
    _refactor_attributes(self, header) :
        Refactor the attributes section to sphinx friendly format.

    _refactor_methods(self, header) :
        Refactor the methods section to sphinx friendly format.

    _refactor_as_items_list(self, header) :
        Refactor the Keywords section to sphinx friendly format.

    _refactor_notes(self, header) :
        Refactor the note section to use the rst ``.. note`` directive.

    _refactor_example(self, header) :
        Refactor the example section to sphinx friendly format.

    """

    def __init__(self, lines, headers=None):

        if headers is None:
            headers = {'Attributes': 'attributes', 'Methods': 'methods',
                       'Notes': 'notes', 'Keywords': 'as_item_list',
                       'Note': 'notes', 'Example': 'example',
                       'Examples': 'example'}

        super(ClassDoc, self).__init__(lines, headers)
        return

    def _refactor_attributes(self, header):
        """Refactor the attributes section to sphinx friendly format"""
        items = self.extract_items(AttributeItem)
        lines = []
        for item in items:
            lines += item.to_rst()
        return lines

    def _refactor_methods(self, header):
        """Refactor the methods section to sphinx friendly format.

        """
        items = self.extract_items(MethodItem)
        lines = []
        if len(items) > 0 :
            columns = self._get_column_lengths(items)
            border = '{0:=^{1}} {0:=^{2}}'.format('', columns[0], columns[1])
            heading = '{0:<{2}} {1:<{3}}'.format('Method', 'Description',
                                                 columns[0], columns[1])
            lines += [border]
            lines += [heading]
            lines += [border]
            for items in items:
                lines += items.to_rst(columns)
            lines += [border]
            lines += ['']
        lines = [line.rstrip() for line in lines]
        return lines

    def _refactor_notes(self, header):
        """Refactor the note section to use the rst ``.. note`` directive.

        """
        paragraph = self.get_next_paragraph()
        lines = ['.. note::']
        lines += add_indent(paragraph)
        return lines

    def _refactor_as_item_list(self, header):
        """ Refactor the a section to sphinx friendly item list.

        Arguments
        ---------
        header : str
            The header name that is used for the fields (i.e. ``:<header>:``).

        """
        items = self.extract_items(item_class=ListItem)
        lines = [':{0}:'.format(header.lower()), '']
        prefix = None if len(items) == 1 else '-'
        for item in items:
            lines += add_indent(item.to_rst(prefix))
        return lines

    def _refactor_example(self, header) :
        """ Refactor the example section to sphinx friendly format.

        Arguments
        ---------
        header : str
            The header name that is used for the fields (i.e. ``:<header>:``).

        """
        paragraph = self.get_next_paragraph()
        lines = ['.. rubric:: {0}'.format(header), '', '::', '']
        lines += add_indent(paragraph)
        return lines


    def _get_column_lengths(self, items):
        """ Helper function to estimate the column widths for the refactoring of
        the ``Methods`` section.

        The method finds the index of the item that has the largest function
        name (i.e. self.term) and the largest signature. If the indexes are not
        the same then checks to see which of the two items have the largest
        string sum (i.e. self.term + self.signature).

        """
        name_index = max_attribute_index(items, 'term')
        signature_index = max_attribute_index(items, 'signature')
        if signature_index != name_index:
            index = signature_index
            item1_width = len(items[index].term + items[index].signature)
            index = name_index
            item2_width = len(items[index].term + items[index].signature)
            first_column = max(item1_width, item2_width)
        else:
            index = name_index
            first_column = len(items[index].term + items[index].signature)

        first_column += 11  # Add boilerplate characters
        second_column = max_attribute_length(items, 'definition')
        return (first_column, second_column)
