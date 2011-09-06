import wx

from duck.frontend.wxwidgets.nicelist import NiceListSearchableCtrl

class PlaylistCtrl(NiceListSearchableCtrl):

    def __init__(self, *args, **kwargs):
        kwargs['columns'] = (('Pos',       50),
                             ('Artist',    200),
                             ('Title',     200),
                             ('Duration',  100))
        kwargs['search_columns'] = [1, 2]
        NiceListSearchableCtrl.__init__(self, 
                                        *args, **kwargs)
        # The wx.App object must be created first for this to work!
        self.NORMAL_FONT = wx.Font(10, wx.FONTFAMILY_DEFAULT,
                                   wx.FONTSTYLE_NORMAL, wx.NORMAL)
        self.BOLD_FONT   = wx.Font(10, wx.FONTFAMILY_DEFAULT,
                                   wx.FONTSTYLE_NORMAL, wx.BOLD)

    def initialize(self, main_window):
        self.main_window = main_window
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.do_change_song)

    def refresh(self):
        data = []
        for row, song in enumerate(self.main_window.backend.playlist.songs):
            data.append((
                str(song.pos + 1),
                song.artist,
                song.title,
                str(song.time),
            ))
        self.load_data(data)

    def change_song(self, old_song, new_song):
        new_pos = long(new_song.pos)
        if old_song is not None:
            old_pos = long(old_song.pos)
            self.SetItemFont(old_pos, self.NORMAL_FONT)
        self.SetItemFont(new_pos, self.BOLD_FONT)
        self.SetItemState(new_pos, wx.LIST_STATE_FOCUSED, wx.LIST_STATE_FOCUSED)
        self.EnsureVisible(new_pos)
 
    def do_change_song(self, event):
        self.main_window.do_change_song(self.get_real_position(event.m_itemIndex))

    def on_list_item_right_click(self, event):
        pass


