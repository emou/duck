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

class SearchField(wx.TextCtrl):
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent)
        self.Bind(wx.EVT_CHAR, self.incremental_search)
        self.search_term = ''
        self.lst = parent
    
    def incremental_search(self, evt):
        key_code = evt.GetKeyCode()
        try:
            char = chr(key_code)
        except ValueError:
            # XXX: Switch to logging.
            print 'WARNING: Ignoring unimplemented key code %s' % evt.GetKeyCode()
            return
        char = char.strip()
        if char:
            # Don't append whitespace.
            self.search_term += char
        if self.search_term:
            self.lst.filter_items(self.search_term)

app = wx.App(False)

class ListCtrlIncrementalSearchMixin(object):

    def __init__(self, search_columns, data=None):
        """
        Initializes a new ListIncrementalSearchMixin.
        `data` is a list of tuples. Each element of the list is a row. An
        element of each tuple corresponds a the column, i.e. something like:
        [(cell00, cell01), (cell10, cell11), ...]

        `search_columns` is a list of values convertable to int, representing
        the indexes of the columns which we should search.

        """
        if self.GetColumnCount() == 0:
            raise ValueError(
                'ListCtrlIncrementalSearchMixin expects you to '
                'create your columns before calling __init__.'
            )
        if self.IsVirtual():
            raise ValueError(
                'ListCtrlIncrementalSearchMixin works on non-virtual '
                'lists only (set wx.LC_VIRTUAL style)'
            )
        if not self.HasFlag(wx.LC_REPORT):
            raise ValueError(
                'ListCtrlIncrementalSearchMixin works on lists in '
                'report view only (set wx.LC_REPORT style)'
            )
        try:
            self.search_columns = map(int, search_columns)
        except ValueError:
            raise ValueError(
                'search_columns should be a list of zero-based '
                'indexes of columns that we should search for'
            )
        self.Bind(wx.EVT_CHAR, self.incremental_search)
        self.search_field = SearchField(self)
        self.data = data
        self.filtered_items = None
        self.all_items = []

        if self.data:
            for row, d in enumerate(self.data):
                item = wx.ListItem()
                item.SetId(row)
                self.InsertItem(item)
                for col, val in enumerate(d):
                    self.SetStringItem(row, col, val)

    def incremental_search(self, evt):
        key_code = evt.GetKeyCode()
        try:
            char =  chr(key_code)
        except ValueError:
            # XXX: Switch to logging.
            print 'WARNING: Ignoring unimplemented key code %s' % evt.GetKeyCode()
            return

        # TODO: handle escape and/or change of focus
        if char == '/':
            self.search_field.Show()
        else:
            evt.Skip()
 
    def filter_items(self, search_term):
        """
        Filters the items in the list, searching for `search_term`
        in columns with indexes in `search_colmns`.
        """
        self.filtered_items = []
        self.all_items = []

        for c in self.search_columns:
            for i in range(self.GetItemCount()):
                item = self.GetItem(i, c)
                self.all_items.append(item)
                if search_term.lower() in item.GetText().lower():
                    self.filtered_items.append(item)
        self.DeleteAllItems()
        for row, item in enumerate(self.filtered_items):
            item.SetId(row)
            self.InsertItem(item)


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
