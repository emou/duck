import wx

class ArtistListCtrl(wx.ListCtrl):
    def initialize(self, main_window):
        self.main_window = main_window
        self.InsertColumn(0, 'Artist')
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.main_window.do_filter_artist)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.main_window.do_add_artist)

    def refresh(self):
        self.DeleteAllItems()
        for row, a in enumerate(sorted(self.main_window.backend.list('artist'))):
            item = wx.ListItem()
            item.SetId(row + 1)
            item.SetText(a)
            self.InsertItem(item)
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
