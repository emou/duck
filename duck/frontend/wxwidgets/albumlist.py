import wx

from duck.frontend.wxwidgets.ducklist import DuckSingleColumnListCtrl

class AlbumListCtrl(DuckSingleColumnListCtrl):

    def initialize(self, main_window):
        self.main_window = main_window
        self.InsertColumn(0, 'Album')
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.main_window.do_filter_album)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.main_window.do_add_album)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.item_right_click)

    def refresh(self):
        pass

    def item_right_click(self, event):
        pass
