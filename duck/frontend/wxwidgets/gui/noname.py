# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Sep  6 2011)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

from duck.frontend.wxwidgets.playlist import PlaylistCtrl
from duck.frontend.wxwidgets.artistlist import ArtistListCtrl
from duck.frontend.wxwidgets.albumlist import AlbumListCtrl
from duck.frontend.wxwidgets.songlist import SongListCtrl
import wx

###########################################################################
## Class MainWindow
###########################################################################

class MainWindow ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Duck MPD client", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_FRAME_STYLE|wx.SYSTEM_MENU|wx.TAB_TRAVERSAL, name = u"duck" )
		
		self.SetSizeHintsSz( wx.Size( -1,-1 ), wx.DefaultSize )
		
		main_sizer = wx.FlexGridSizer( 1, 1, 0, 0 )
		main_sizer.AddGrowableCol( 0 )
		main_sizer.AddGrowableRow( 0 )
		main_sizer.AddGrowableRow( 1 )
		main_sizer.SetFlexibleDirection( wx.BOTH )
		main_sizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_ALL )
		
		main_sizer.SetMinSize( wx.Size( 600,400 ) ) 
		self.notebook = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		notebookImageSize = wx.Size( 24,24 )
		notebookIndex = 0
		notebookImages = wx.ImageList( notebookImageSize.GetWidth(), notebookImageSize.GetHeight() )
		self.notebook.AssignImageList( notebookImages )
		self.now_playing_page = wx.Panel( self.notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		now_playing_sizer = wx.FlexGridSizer( 3, 1, 0, 0 )
		now_playing_sizer.AddGrowableCol( 0 )
		now_playing_sizer.AddGrowableRow( 3 )
		now_playing_sizer.SetFlexibleDirection( wx.BOTH )
		now_playing_sizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_ALL )
		
		playing_buttons_sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.previous_button = wx.BitmapButton( self.now_playing_page, wx.ID_ANY, wx.Bitmap( u"duck/images/media-skip-backward-5.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		playing_buttons_sizer.Add( self.previous_button, 0, 0, 5 )
		
		self.play_button = wx.BitmapButton( self.now_playing_page, wx.ID_ANY, wx.Bitmap( u"duck/images/media-playback-start-5.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		playing_buttons_sizer.Add( self.play_button, 0, 0, 5 )
		
		self.pause_button = wx.BitmapButton( self.now_playing_page, wx.ID_ANY, wx.Bitmap( u"duck/images/media-playback-pause-5.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		playing_buttons_sizer.Add( self.pause_button, 0, 0, 5 )
		
		self.stop_buton = wx.BitmapButton( self.now_playing_page, wx.ID_ANY, wx.Bitmap( u"duck/images/media-playback-stop-5.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		playing_buttons_sizer.Add( self.stop_buton, 0, 0, 5 )
		
		self.next_button = wx.BitmapButton( self.now_playing_page, wx.ID_ANY, wx.Bitmap( u"duck/images/media-skip-forward-5.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		playing_buttons_sizer.Add( self.next_button, 0, 0, 5 )
		
		volume_sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		
		volume_sizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.volume_slider = wx.Slider( self.now_playing_page, wx.ID_ANY, 50, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
		self.volume_slider.SetMinSize( wx.Size( 150,-1 ) )
		
		volume_sizer.Add( self.volume_slider, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.volume_bitmap = wx.StaticBitmap( self.now_playing_page, wx.ID_ANY, wx.Bitmap( u"duck/images/player-volume-2.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
		volume_sizer.Add( self.volume_bitmap, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		self.clear_button = wx.BitmapButton( self.now_playing_page, wx.ID_ANY, wx.Bitmap( u"duck/images/playlist-clear.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		volume_sizer.Add( self.clear_button, 0, 0, 5 )
		
		playing_buttons_sizer.Add( volume_sizer, 1, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		now_playing_sizer.Add( playing_buttons_sizer, 1, wx.EXPAND, 5 )
		
		self.progress_slider = wx.Slider( self.now_playing_page, wx.ID_ANY, 50, 0, 100, wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
		now_playing_sizer.Add( self.progress_slider, 0, wx.BOTTOM|wx.EXPAND, 5 )
		
		self.playlist_search = wx.TextCtrl( self.now_playing_page, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB )
		now_playing_sizer.Add( self.playlist_search, 0, wx.EXPAND, 5 )
		
		self.playlist = PlaylistCtrl( self.now_playing_page, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		now_playing_sizer.Add( self.playlist, 1, wx.EXPAND, 5 )
		
		self.now_playing_page.SetSizer( now_playing_sizer )
		self.now_playing_page.Layout()
		now_playing_sizer.Fit( self.now_playing_page )
		self.notebook.AddPage( self.now_playing_page, u"Now playing", False )
		self.library_page = wx.Panel( self.notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer9 = wx.BoxSizer( wx.VERTICAL )
		
		self.library_search_field = wx.TextCtrl( self.library_page, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB )
		bSizer9.Add( self.library_search_field, 0, wx.ALL|wx.EXPAND, 5 )
		
		library_sizer = wx.FlexGridSizer( 2, 2, 0, 0 )
		library_sizer.AddGrowableCol( 0 )
		library_sizer.AddGrowableCol( 1 )
		library_sizer.AddGrowableRow( 0 )
		library_sizer.AddGrowableRow( 1 )
		library_sizer.SetFlexibleDirection( wx.BOTH )
		library_sizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_ALL )
		
		self.artist_list = ArtistListCtrl( self.library_page, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_NO_HEADER|wx.LC_REPORT )
		library_sizer.Add( self.artist_list, 1, wx.EXPAND, 5 )
		
		self.album_list = AlbumListCtrl( self.library_page, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_ICON|wx.LC_NO_HEADER|wx.LC_REPORT )
		library_sizer.Add( self.album_list, 1, wx.EXPAND, 5 )
		
		self.song_list = SongListCtrl( self.library_page, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_ICON|wx.LC_NO_HEADER|wx.LC_REPORT )
		library_sizer.Add( self.song_list, 0, wx.EXPAND, 5 )
		
		bSizer9.Add( library_sizer, 1, wx.EXPAND, 5 )
		
		self.library_page.SetSizer( bSizer9 )
		self.library_page.Layout()
		bSizer9.Fit( self.library_page )
		self.notebook.AddPage( self.library_page, u"Library", True )
		self.devices_page = wx.Panel( self.notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.notebook.AddPage( self.devices_page, u"External devices", False )
		
		main_sizer.Add( self.notebook, 1, wx.EXPAND, 5 )
		
		self.SetSizer( main_sizer )
		self.Layout()
		main_sizer.Fit( self )
		self.main_menu = wx.MenuBar( 0 )
		self.menu_music = wx.Menu()
		self.item_rescan = wx.MenuItem( self.menu_music, wx.ID_ANY, u"&Rescan database", wx.EmptyString, wx.ITEM_NORMAL )
		self.menu_music.AppendItem( self.item_rescan )
		
		self.main_menu.Append( self.menu_music, u"&Music" ) 
		
		self.menu_settings = wx.Menu()
		self.item_configure = wx.MenuItem( self.menu_settings, wx.ID_ANY, u"&Configure Duck...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menu_settings.AppendItem( self.item_configure )
		
		self.main_menu.Append( self.menu_settings, u"&Settings" ) 
		
		self.SetMenuBar( self.main_menu )
		
		self.status_bar = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.previous_button.Bind( wx.EVT_BUTTON, self.do_previous )
		self.play_button.Bind( wx.EVT_BUTTON, self.do_play )
		self.pause_button.Bind( wx.EVT_BUTTON, self.do_pause )
		self.stop_buton.Bind( wx.EVT_BUTTON, self.do_stop )
		self.next_button.Bind( wx.EVT_BUTTON, self.do_next )
		self.clear_button.Bind( wx.EVT_BUTTON, self.do_clear )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def do_previous( self, event ):
		event.Skip()
	
	def do_play( self, event ):
		event.Skip()
	
	def do_pause( self, event ):
		event.Skip()
	
	def do_stop( self, event ):
		event.Skip()
	
	def do_next( self, event ):
		event.Skip()
	
	def do_clear( self, event ):
		event.Skip()
	

