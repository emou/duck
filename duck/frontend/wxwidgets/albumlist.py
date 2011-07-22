import wx

from duck.frontend.wxwidgets.nicelist import NiceListCtrl

class AlbumListCtrl(NiceListCtrl):

    def initialize(self, main_window):
        self.main_window = main_window
        self.InsertColumn(0, 'Album')
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.main_window.do_filter_album)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.main_window.do_add_album)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.item_right_click)

    def refresh(self):
        pass

    def load(self, values):
        self.DeleteAllItems()
        for row, a in enumerate(values):
                item = wx.ListItem()
                item.SetId(row + 1)
                item.SetText(a)
                self.InsertItem(item)

    def item_right_click(self, event):
        pass
