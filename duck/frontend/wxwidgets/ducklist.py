import wx

class Column(object):
    """
    Column objects should passed to
    """
    resizeable = True
    def __init__(self, name, initial_width=None):
        self.name = name
        self.initial_width = initial_width

class FixedWidthColumn(Column):
    """
    Ignores width adjustment
    """
    resizeable = False

class _ListCtrlIncrementalSearchMixin(object):
    """
    WARNING: class internal to this module.
    """
    SEARCH_KEY = ord('/')

    def __init__(self, search_field, columns, search_columns):
        """
        Initializes a new _ListCtrlIncrementalSearchMixin.
        `search_field` is a SearchField instance to which we should attach.
        Letting users pass this as a parameter lets them create it however they want.

        `data` is a list of tuples. Each element of the list is a row. An
        element of each tuple corresponds a the column, i.e. something like:
        [(cell00, cell01), (cell10, cell11), ...]

        `search_columns` is a list of values convertable to int, representing
        the indexes of the columns which we should search.

        NOTE: The OnGetItem* methods that are to be defined for virutal lists
        will be replaced in the derived class.

        """
        self.NORMAL_FONT = wx.Font(10, wx.FONTFAMILY_DEFAULT,
                                   wx.FONTSTYLE_NORMAL, wx.NORMAL)
        # The only way I was able to find to actually guarantee that these
        # methods will be looked up from our mixin.
        self.__class__.OnGetItemText = _ListCtrlIncrementalSearchMixin.OnGetItemText
        self.__class__.OnGetItemImage = _ListCtrlIncrementalSearchMixin.OnGetItemImage
        self.__class__.OnGetItemAttr = _ListCtrlIncrementalSearchMixin.OnGetItemAttr

        if not self.HasFlag(wx.LC_VIRTUAL):
            raise ValueError(
                '_ListCtrlIncrementalSearchMixin works on virtual '
                'lists only (set wx.LC_VIRTUAL style)'
            )
        if not self.HasFlag(wx.LC_REPORT):
            raise ValueError(
                '_ListCtrlIncrementalSearchMixin works on lists in '
                'report view only (set wx.LC_REPORT style)'
            )
        try:
            self.search_columns = map(int, search_columns)
        except ValueError:
            raise ValueError(
                'search_columns should be a list of zero-based '
                'indexes of columns that we should search for'
            )
        self.columns = columns
        for i, col in enumerate(columns):
            if col.initial_width is not None:
                self.InsertColumn(i, col.name, col.initial_width)
            else:
                self.InsertColumn(i, col.name)
        if search_field is not None:
            self.set_search_field(search_field)
        else:
            self.search_field = None
        self.Bind(wx.EVT_CHAR, self.on_char)
        self.search_term = ''
        self.filtered = None
        self.attrs = {}

    def set_search_field(self, search_field):
        self.search_field = search_field
        self.search_field.Bind(wx.EVT_TEXT, self.on_text_in_field)
        self.search_field.Bind(wx.EVT_CHAR, self.on_char_in_field)
        self.search_field.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter_in_field)

    def load_data(self, data):
        self.data = data
        if self.data is not None:
            self.SetItemCount(len(self.data))
        else:
            self.SetItemCount(0)
        if self.search_term:
            self.filter_items(self.search_term)
        else:
            self.filtered=None

    def on_char_in_field(self, evt):
        key_code = evt.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
            # Escape key. Cancel
            self.incremental_search_stop()
        else:
            evt.Skip()

    def on_char(self, evt):
        key_code = evt.GetKeyCode()
        if key_code == self.SEARCH_KEY:
            self.search_field.SetFocus()

    def on_text_in_field(self, evt):
        self.search_term = evt.GetString()
        self.filter_items(self.search_term)
        evt.Skip()
    
    def on_text_enter_in_field(self, evt):
        """
        Implement in subclass.
        """
        pass

    def incremental_search_stop(self):
        """
        Cancel the search load back all of the items.
        """
        self.search_field.ChangeValue('')
        self.filtered = None
        self.SetItemCount(len(self.data))
    
    def filter_items(self, search_term):
        """
        Filters the items in the list, searching for `search_term`
        in columns with indexes in `search_colmns`.
        """
        if not search_term:
            self.incremental_search_stop()
        self.filtered = []
        for i, columns in enumerate(self.data):
            for c in self.search_columns:
                if search_term.lower() in unicode(columns[c].lower(), encoding='utf-8'):
                    self.filtered.append(i)
                    break
        # Clear selected items
        for i in self.get_selected_items():
            self.SetItemState(i, 0, wx.LIST_STATE_SELECTED, convert=False)
        # Set focus to and select the first item
        self.SetItemState(0, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED, convert=False)
        self.SetItemState(0, wx.LIST_STATE_FOCUSED, wx.LIST_STATE_FOCUSED, convert=False)
        self.SetItemCount(len(self.filtered))

    def _get_item(self, item):
        if self.filtered is not None:
            return self.data[self.filtered[item]]
        return self.data[item]
    
    def SetItemFont(self, item, font):
        itemAttr = self.attrs.setdefault(item, wx.ListItemAttr())
        itemAttr.SetFont(font)
        self.Refresh()
    
    def SetItemState(self, item, st, st_mask, convert=True):
        if convert:
            item = self.get_reverse_position(item)
        return super(_ListCtrlIncrementalSearchMixin, self).SetItemState(item, st, st_mask)

    def EnsureVisible(self, item, convert=True):
        if convert:
            item = self.get_reverse_position(item)
        super(_ListCtrlIncrementalSearchMixin, self).EnsureVisible(item)

    def GetItemFont(self, item, convert=True):
        if convert:
            item = self.get_reverse_position(item)
        itemAttr = self.attrs.get(item, None)
        if itemAttr is not None:
            return itemAttr.GetFont()
        return self.NORMAL_FONT

    def GetItemText(self, item, col=0):
        return self._get_item(item)[col]
 
    # Virtual list callbacks
    def OnGetItemText(self, item, col):
        return self._get_item(item)[col]

    def OnGetItemImage(self, item):
        return -1

    def OnGetItemAttr(self, item):
        return self.attrs.get(self.get_real_position(item))

    def get_real_position(self, pos):
        if self.filtered is None:
            return pos
        return self.filtered[pos]

    def get_reverse_position(self, pos):
        if self.filtered is None:
            return pos
        return self.filtered.index(pos)

    def get_selected_items(self):
        """
        Returns the indexes of all selected items in the control.
        """
        indexes = []
        lastFound = -1
        while True:
            index = self.GetNextItem(lastFound, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if index == -1:
                break
            else:
                lastFound = index
                indexes.append(index)
        return indexes


class _ListCtrlAutoRelativeWidthMixin(object):
    """
        WARNING: class internal to this module.

        Uses wx.LIST_AUTOSIZE internally. Then just expands the columns keeping
        their relative sizes.

        NOTE:    This only works for report-style lists.

        WARNING: If you override the EVT_SIZE event in your wx.ListCtrl, make
                 sure you call event.Skip() to ensure that the mixin's
                 _OnResize method is called.
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

        has_columns = hasattr(self, 'columns')
        numCols = self.GetColumnCount()

        # XXX: Cleanup this check.
        if has_columns:
            assert len(self.columns) == numCols
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

        if has_columns:
            total_resizeable = 0
            free_width = listWidth
            for i, c in enumerate(self.columns):
                w = self.GetColumnWidth(i)
                if c.resizeable:
                    total_resizeable += w
                free_width -= w

            for i, c in enumerate(self.columns):
                if c.resizeable:
                    w = self.GetColumnWidth(i)
                    self.SetColumnWidth(i, w + free_width*w/total_resizeable)
        else:
            # XXX: Cleanup this branch.
            totColWidth = sum(self.GetColumnWidth(col) for col in range(numCols))
            totColWidth = max(1, totColWidth)
            freeWidth = listWidth - totColWidth

            for c in range(numCols):
                w = self.GetColumnWidth(c)
                self.SetColumnWidth(c, w + freeWidth*w/totColWidth)

class DuckListCtrl(wx.ListCtrl, _ListCtrlAutoRelativeWidthMixin):

    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        _ListCtrlAutoRelativeWidthMixin.__init__(self)


class DuckListSearchableCtrl(_ListCtrlIncrementalSearchMixin, wx.ListCtrl, _ListCtrlAutoRelativeWidthMixin):

    def __init__(self, *args, **kwargs):
        # Ensure we're using a virtual list in report view.
        if len(args) > 4:
            args = list(args)
            args[4] |= wx.LC_VIRTUAL | wx.LC_REPORT
        else:
            kwargs['style'] = kwargs.get('style', 0) | wx.LC_VIRTUAL | wx.LC_REPORT
        search_field = kwargs.pop('search_field', None)
        search_columns = kwargs.pop('search_columns')
        columns = kwargs.pop('columns')
        wx.ListCtrl.__init__(self, *args, **kwargs)
        _ListCtrlAutoRelativeWidthMixin.__init__(self)
        _ListCtrlIncrementalSearchMixin.__init__(
            self,
            search_field=search_field, 
            columns=columns,
            search_columns=search_columns
        )


class DuckSingleColumnListCtrl(DuckListCtrl):

    def load(self, values):
        """
        Replaces all items with new ones, containing `values`.
        """
        self.DeleteAllItems()
        for row, a in enumerate(values):
            item = wx.ListItem()
            item.SetId(row + 1)
            item.SetText(a)
            self.InsertItem(item)


if __name__ == '__main__':
    app = wx.App()
    frame = wx.Frame(None, wx.ID_ANY, "Test ducklist.py")
    frame.Show()
    win = DuckListSearchableCtrl(frame, search_columns=[0], columns=[Column(name='Foo', initial_width=100)])
    win.load_data([('A',), ('B',), ('C',),])
    app.MainLoop()
