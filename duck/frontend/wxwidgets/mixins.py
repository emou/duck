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
        self.Bind(wx.EVT_CHAR, self.on_char)
        self.Bind(wx.EVT_TEXT, self.on_text)
        self.search_term = ''
        self.lst = parent
    
    def on_char(self, evt):
        print 'Incremental...'
        key_code = evt.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
            # Escape key. Cancel
            self.Hide()
            self.lst.incremental_search_stop()
            return
        try:
            char = chr(key_code)
        except ValueError:
            # XXX: Switch to logging.
            print 'WARNING: Ignoring unimplemented key code %s' % evt.GetKeyCode()
            evt.Skip()
            return
        self.search_term += char
        # Strip whitespace
        self.search_term = self.search_term.strip()
        if self.search_term:
            self.lst.filter_items(self.search_term)
        evt.Skip()
    
    def on_text(self, evt):
        self.search_term = evt.GetString()
        self.lst.filter_items(self.search_term)
        evt.Skip()


class ListCtrlIncrementalSearchMixin(object):

    def __init__(self, columns, search_columns, data=None):
        """
        Initializes a new ListIncrementalSearchMixin.
        `data` is a list of tuples. Each element of the list is a row. An
        element of each tuple corresponds a the column, i.e. something like:
        [(cell00, cell01), (cell10, cell11), ...]

        `search_columns` is a list of values convertable to int, representing
        the indexes of the columns which we should search.

        NOTE: The OnGetItem* methods that are to be defined for virutal lists
        will be replaced in the derived class.

        """
        # The only way I was able to find to actually guarantee that these
        # methods will be looked up from our mixin.
        self.__class__.OnGetItemText = ListCtrlIncrementalSearchMixin.OnGetItemText
        self.__class__.OnGetItemImage = ListCtrlIncrementalSearchMixin.OnGetItemImage
        self.__class__.OnGetItemAttr = ListCtrlIncrementalSearchMixin.OnGetItemAttr

        if not self.HasFlag(wx.LC_VIRTUAL):
            raise ValueError(
                'ListCtrlIncrementalSearchMixin works on virtual '
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
        for i, col in enumerate(columns):
            self.InsertColumn(i, col[0]) #, col[1])
        # XXX: Move up as a main window / parent event?
        self.Bind(wx.EVT_CHAR, self.on_char)
        self.search_field = SearchField(self)
        self.filtered = None
        self.attrs = {}
        self.load_data(data)
    
    def load_data(self, data):
        self.data = data
        if self.data is not None:
            self.SetItemCount(len(self.data))
        else:
            self.SetItemCount(0)

    def on_char(self, evt):
        self.search_field.ProcessEvent(evt)

    def incremental_search_stop(self):
        """
        Cancel the search load back all of the items.
        """
        self.filtered = None
        self.SetItemCount(len(self.data))
 
    def filter_items(self, search_term):
        """
        Filters the items in the list, searching for `search_term`
        in columns with indexes in `search_colmns`.
        """
        if not search_term:
            self.filtered = self.incremental_search_stop()
        if self.filtered is not None:
            search_range = list(self.filtered)
        else:
            search_range = range(len(self.data))
        self.filtered = []
        for i in search_range:
            columns = self.data[i]
            for c in self.search_columns:
                if search_term.lower() in columns[c].lower():
                    self.filtered.append(i)
                    break
        self.SetItemCount(len(self.filtered))

    def _get_item(self, item):
        if self.filtered is not None:
            return self.data[self.filtered[item]]
        return self.data[item]
    
    def SetItemFont(self, item, font, absolute=True):
        """
        The `absolute` argument defines whether the item's index
        is absolute and should be converted to fit in the filtered.
        """
        if absolute:
            item = self.get_reverse_position(item)
        itemAttr = self.attrs.setdefault(item, wx.ListItemAttr())
        itemAttr.SetFont(font)
        self.Refresh()
    
    def GetItemFont(self, item, absolute=True):
        if absolute:
            item = self.get_reverse_position(item)
        ret = self.attrs.get(item, wx.Font())
        return ret

    def GetItemText(self, item, col):
        return self._get_item(item)[col]
 
    # Virtual list callbacks
    def OnGetItemText(self, item, col):
        return self._get_item(item)[col]

    def OnGetItemImage(self, item):
        return -1

    def OnGetItemAttr(self, item):
        return self.attrs.get(item)
    
    def get_real_position(self, pos):
        if self.filtered is None:
            return pos
        return self.filtered[pos]
    
    def get_reverse_position(self, pos):
        if self.filtered is None:
            return pos
        try:
            return self.filtered.index(pos - 1)
        except:
            print self.filtered
            raise


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
