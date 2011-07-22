import wx
import duck.frontend.wxwidgets

class ArtistContextMenu(wx.Menu):
    ADD_ID = 1
    REPLACE_ID = 2

    def __init__(self, artist, main_window, *args, **kwargs):
        wx.Menu.__init__(self, *args, **kwargs)
        self.artist = artist
        self.main_window = main_window
        self.Append(self.ADD_ID, '&Add to playlist')
        self.Append(self.REPLACE_ID, '&Replace playlist')
        self.Connect(-1, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.on_select)

    def on_select(self, event):
        eid = event.GetId()
        if eid==self.ADD_ID:
            with self.main_window.backend:
                self.main_window.backend.add_artist(self.artist)
        elif eid==self.REPLACE_ID:
            with self.main_window.backend:
                self.main_window.backend.replace_artist(self.artist)
        else:
            return
        wx.PostEvent(self.main_window, duck.frontend.wxwidgets.ChangesEvent(['playlist']))

class ArtistListCtrl(wx.ListCtrl):


    def initialize(self, main_window):
        self.main_window = main_window
        self.InsertColumn(0, 'Artist')
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.main_window.do_filter_artist)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.main_window.do_add_artist)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_list_item_right_click)

    def refresh(self):
        self.DeleteAllItems()
        for row, a in enumerate(sorted(self.main_window.backend.list('artist'))):
            item = wx.ListItem()
            item.SetId(row + 1)
            item.SetText(a)
            self.InsertItem(item)
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)

    def on_list_item_right_click(self, event):
        menu = ArtistContextMenu(artist = event.Item.GetText(),
                                 main_window = self.main_window)
        self.main_window.PopupMenu(menu)


