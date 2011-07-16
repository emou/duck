import wx

class PlaylistCtrl(wx.ListCtrl):


    def initialize(self, main_window):
       self.main_window = main_window

       # The wx.App object must be created first!
       self.NORMAL_FONT = wx.Font(10, wx.FONTFAMILY_DEFAULT,
                                  wx.FONTSTYLE_NORMAL, wx.NORMAL)
       self.BOLD_FONT   = wx.Font(10, wx.FONTFAMILY_DEFAULT,
                                  wx.FONTSTYLE_NORMAL, wx.BOLD)

       for (i,col) in enumerate((('Pos',       50),
                                 ('Artist',    200),
                                 ('Title',     200),
                                 ('Duration',  100))):
           self.InsertColumn(i, col[0], width=col[1])

       self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.main_window.do_change_song)


    def refresh(self):

        self.DeleteAllItems()

        current_song = self.main_window.backend.current_song

        for row, song in enumerate(self.main_window.backend.playlist.songs):
            item = wx.ListItem()
            item.SetData(long(song.id))
            item.SetId(row + 1)

            idx = self.InsertItem(item)
            self.SetStringItem(idx, 0, str(song.pos + 1))
            self.SetStringItem(idx, 1, song.artist)
            self.SetStringItem(idx, 2, song.title)
            self.SetStringItem(idx, 3, str(song.time))


    def change_song(self, old_song, new_song):
        new_pos = long(new_song.pos)
        if old_song is not None:
            old_pos = long(old_song.pos)
            self.SetItemFont(old_pos, self.NORMAL_FONT)
        self.SetItemFont(new_pos, self.BOLD_FONT)
        self.SetItemState(new_pos, wx.LIST_STATE_FOCUSED, wx.LIST_STATE_FOCUSED)
        self.EnsureVisible(new_pos)
