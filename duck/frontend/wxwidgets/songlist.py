import wx

from duck.frontend.wxwidgets.nicelist import NiceListCtrl

class SongListCtrl(NiceListCtrl):

    def initialize(self, main_window):
        self.main_window = main_window
        self.InsertColumn(0, 'Song')

    def refresh(self):
        pass

    def load(self, values):
        self.DeleteAllItems()
        for row, a in enumerate(values):
                item = wx.ListItem()
                item.SetId(row + 1)
                item.SetText(a)
                self.InsertItem(item)

    def on_list_item_right_click(self, event):
        pass
