import wx

from duck.frontend.wxwidgets.mixins import ListCtrlAutoRelativeWidthMixin

class NiceListCtrl(wx.ListCtrl, ListCtrlAutoRelativeWidthMixin):

    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        ListCtrlAutoRelativeWidthMixin.__init__(self)

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


