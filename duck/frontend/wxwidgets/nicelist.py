import wx

from duck.frontend.wxwidgets.mixins import ListCtrlAutoRelativeWidthMixin, ListCtrlIncrementalSearchMixin

class NiceListCtrl(wx.ListCtrl, ListCtrlAutoRelativeWidthMixin):

    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        ListCtrlAutoRelativeWidthMixin.__init__(self)


class NiceListSearchableCtrl(ListCtrlIncrementalSearchMixin, wx.ListCtrl, ListCtrlAutoRelativeWidthMixin):

    def __init__(self, *args, **kwargs):
        # Ensure we're using a virtual list in report view.
        if len(args) > 4:
            args = list(args)
            args[4] |= wx.LC_VIRTUAL | wx.LC_REPORT
        else:
            kwargs['style'] = kwargs.get('style', 0) | wx.LC_VIRTUAL | wx.LC_REPORT
        search_field = kwargs.pop('search_field')
        search_columns = kwargs.pop('search_columns')
        columns = kwargs.pop('columns')
        wx.ListCtrl.__init__(self, *args, **kwargs)
        ListCtrlAutoRelativeWidthMixin.__init__(self)
        ListCtrlIncrementalSearchMixin.__init__(
            self,
            search_field=search_field, 
            columns=columns,
            search_columns=search_columns
        )


class NiceSingleColumnListCtrl(NiceListCtrl):

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
    frame = wx.Frame(None, wx.ID_ANY, "Test nicelist.py")
    frame.Show()
    win = NiceListSearchableCtrl(frame, search_columns=[0], columns=[('Foo', 100)])
    win.load_data([('A',), ('B',), ('C',),])
    app.MainLoop()
