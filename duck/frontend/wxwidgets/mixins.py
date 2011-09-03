# XXX: Not sure if I should mention this here, but parts in this module are a
# rework of wxPython.lib.mixins.listctrl
# TODO: Learn about licenses and if this is needed:
#----------------------------------------------------------------------------
# Name:        wxPython.lib.mixins.listctrl
# Purpose:     Helpful mix-in classes for wxListCtrl
#
# Author:      Robin Dunn
#
# Created:     15-May-2001
# RCS-ID:      $Id: listctrl.py 63322 2010-01-30 00:59:55Z RD $
# Copyright:   (c) 2001 by Total Control Software
# Licence:     wxWindows license
#----------------------------------------------------------------------------

import wx

class SearchForm(wx.TextCtrl):
    pass

class ListCtrlIncrementalSearchMixin:

    def __init__(self):
        self.search_form = SearchForm(self)
        self.Bind(wx.EVT_CHAR, self.incremental_search)
        self.search_term = ''
        self.insert_mode = False

    def incremental_search(self, evt):
        self.search_form.Show()
        key_code = evt.GetKeyCode()
        try:
            char =  chr(key_code)
        except ValueError:
            # XXX: Switch to logging.
            print 'WARNING: Ignoring unimplemented key code %s' % evt.GetKeyCode()
            return

        # TODO: handle escape and/or change of focus
        if char == '/':
            self.insert_mode = True
        elif char.isalnum():
            self.search_term += char
        
        self._search()
    
    def _search(self):
        pass

class ListCtrlAutoRelativeWidthMixin:
    """ A mix-in class that automatically fits columns in a ListCtrl.
        Uses wx.LIST_AUTOSIZE internally. Then just expands the columns keeping
        their relative sizes.

        NOTE:    This only works for report-style lists.

        WARNING: If you override the EVT_SIZE event in your wx.ListCtrl, make
                 sure you call event.Skip() to ensure that the mixin's
                 _OnResize method is called.

        This mix-in class was written by Emil Stanchev <stanchev.emil@gmail.com>
    """
    def __init__(self):
        """ Standard initializer.
        """
        self.Bind(wx.EVT_SIZE, self._onResize)
        self.Bind(wx.EVT_LIST_DELETE_ALL_ITEMS, self._onResize)
        self._doResize()

    # =====================
    # == Private Methods ==
    # =====================

    def _onResize(self, event):
        """
        Respond to the wx.ListCtrl being resized.
        """
        if 'gtk2' in wx.PlatformInfo:
            self._doResize()
        else:
            wx.CallAfter(self._doResize)
        event.Skip()


    def _doResize(self):
        if not self:  # avoid a PyDeadObject error
            return

        if self.GetSize().height < 32:
            return  # avoid an endless update bug when the height is small.
        
        numCols = self.GetColumnCount()
        if numCols == 0:
            return

        # We're showing the vertical scrollbar -> allow for scrollbar width
        # NOTE: on GTK, the scrollbar is included in the client size, but on
        # Windows it is not included
        listWidth = self.GetClientSize().width
        if wx.Platform != '__WXMSW__':
            if self.GetItemCount() > self.GetCountPerPage():
                scrollWidth = wx.SystemSettings_GetMetric(wx.SYS_VSCROLL_X)
                listWidth = listWidth - scrollWidth

        for col in range(numCols):
            self.SetColumnWidth(col, wx.LIST_AUTOSIZE)

        totColWidth = sum(self.GetColumnWidth(col) for col in range(numCols))
        totColWidth = max(1, totColWidth)
        freeWidth = listWidth - totColWidth

        for c in range(numCols):
            w = self.GetColumnWidth(c)
            self.SetColumnWidth(c, w + freeWidth*w/totColWidth)
