import wx
import duck.frontend.wxwidgets

from duck.frontend.wxwidgets.nicelist import NiceListSearchableCtrl

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
                self.main_window.backend.play(0)
        else:
            event.Skip()
        wx.PostEvent(self.main_window,
                     duck.frontend.wxwidgets.ChangesEvent(['playlist']))

class ArtistListCtrl(NiceListSearchableCtrl):
    def __init__(self, *args, **kwargs):
        kwargs['columns'] = (('Artist', None),)
        kwargs['search_columns'] = [0]
        NiceListSearchableCtrl.__init__(self, *args, **kwargs)

    def initialize(self, main_window, *args, **kwargs):
        self.main_window = main_window
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.do_filter_artist)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.do_replace_artist)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_list_item_right_click)

    def refresh(self):
        self.load_data(map(
            lambda x: (x,),
            sorted(self.main_window.backend.list('artist'))
        ))

    def on_list_item_right_click(self, event):
        selected_artist = self._get_artist_from_event(event)
        menu = ArtistContextMenu(artist = selected_artist,
                                 main_window = self.main_window)
        self.main_window.PopupMenu(menu)

    def on_text_enter_in_field(self, event):
        self.do_replace_artist(event)

    def do_filter_artist(self, event):
        selected_artist = event.m_itemIndex
        return self.main_window.do_filter_artist(self.GetItemText(selected_artist))

    def do_replace_artist(self, event):
        with self.main_window.backend:
            self.main_window.backend.replace_artist(
                self._get_artist_from_event(event)
            )
            self.main_window.backend.play(0)
        wx.PostEvent(self.main_window,
                     duck.frontend.wxwidgets.ChangesEvent(['playlist']))
 
    def _get_artist_from_event(self, event):
        return self.GetItemText(self.get_selected_items()[0])
