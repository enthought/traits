#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# 
# Author: Enthought, Inc.
# Description: <Enthought util package component>
#------------------------------------------------------------------------------
'''class ImageRenderer(wxPyGridCellRenderer):
    def __init__(self, table):
        """
        Image Renderer Test.  This just places an image in a cell
        based on the row index.  There are N choices and the
        choice is made by  choice[row%N]
        """
        wxPyGridCellRenderer.__init__(self)
        self.table = table
        self._choices = [images.getSmilesBitmap,
                         images.getMondrianBitmap,
                         images.get_10s_Bitmap,
                         images.get_01c_Bitmap]


        self.colSize = None
        self.rowSize = None

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        choice = self.table.GetRawValue(row, col)
        bmp = self._choices[ choice % len(self._choices)]()
        image = wxMemoryDC()
        image.SelectObject(bmp)

        # clear the background
        dc.SetBackgroundMode(wxSOLID)
        if isSelected:
            dc.SetBrush(wxBrush(wxBLUE, wxSOLID))
            dc.SetPen(wxPen(wxBLUE, 1, wxSOLID))
        else:
            dc.SetBrush(wxBrush(wxWHITE, wxSOLID))
            dc.SetPen(wxPen(wxWHITE, 1, wxSOLID))
        dc.DrawRectangle(rect.x, rect.y, rect.width, rect.height)

        # copy the image but only to the size of the grid cell
        width, height = bmp.GetWidth(), bmp.GetHeight()
        if width > rect.width-2:
            width = rect.width-2

        if height > rect.height-2:
            height = rect.height-2

        dc.Blit(rect.x+1, rect.y+1, width, height,
                image,
                0, 0, wxCOPY, True)'''
