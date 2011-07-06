# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Apr 10 2011)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx

###########################################################################
## Class MainWindow
###########################################################################

class MainWindow ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Duck MPD client", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_FRAME_STYLE|wx.SYSTEM_MENU|wx.TAB_TRAVERSAL, name = u"duck" )
		
		self.SetSizeHintsSz( wx.Size( -1,-1 ), wx.DefaultSize )
		
		main_sizer = wx.FlexGridSizer( 2, 2, 0, 0 )
		main_sizer.AddGrowableCol( 0 )
		main_sizer.AddGrowableRow( 0 )
		main_sizer.SetFlexibleDirection( wx.BOTH )
		main_sizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_ALL )
		
		self.notebook = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		notebookImageSize = wx.Size( 24,24 )
		notebookIndex = 0
		notebookImages = wx.ImageList( notebookImageSize.GetWidth(), notebookImageSize.GetHeight() )
		self.notebook.AssignImageList( notebookImages )
		self.notebook.SetMinSize( wx.Size( 600,400 ) )
		
		self.now_playing_page = wx.Panel( self.notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		now_playing_sizer = wx.FlexGridSizer( 3, 1, 0, 0 )
		now_playing_sizer.AddGrowableCol( 0 )
		now_playing_sizer.AddGrowableCol( 1 )
		now_playing_sizer.AddGrowableCol( 2 )
		now_playing_sizer.AddGrowableRow( 2 )
		now_playing_sizer.SetFlexibleDirection( wx.BOTH )
		now_playing_sizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_ALL )
		
		playing_buttons_sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.previous_button = wx.BitmapButton( self.now_playing_page, wx.ID_ANY, wx.Bitmap( u"duck/images/media-seek-backward-5.ico", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		playing_buttons_sizer.Add( self.previous_button, 0, wx.ALL, 5 )
		
		self.play_button = wx.BitmapButton( self.now_playing_page, wx.ID_ANY, wx.Bitmap( u"duck/images/media-playback-start-5.ico", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		playing_buttons_sizer.Add( self.play_button, 0, wx.ALL, 5 )
		
		self.pause_button = wx.BitmapButton( self.now_playing_page, wx.ID_ANY, wx.Bitmap( u"duck/images/media-playback-pause-5.ico", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		playing_buttons_sizer.Add( self.pause_button, 0, wx.ALL, 5 )
		
		self.stop_buton = wx.BitmapButton( self.now_playing_page, wx.ID_ANY, wx.Bitmap( u"duck/images/media-playback-stop-5.ico", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		playing_buttons_sizer.Add( self.stop_buton, 0, wx.ALL, 5 )
		
		self.next_button = wx.BitmapButton( self.now_playing_page, wx.ID_ANY, wx.Bitmap( u"duck/images/media-seek-forward-5.ico", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		playing_buttons_sizer.Add( self.next_button, 0, wx.ALL, 5 )
		
		volume_sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.volume_slider = wx.Slider( self.now_playing_page, wx.ID_ANY, 50, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
		self.volume_slider.SetMinSize( wx.Size( 150,-1 ) )
		
		volume_sizer.Add( self.volume_slider, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		playing_buttons_sizer.Add( volume_sizer, 1, wx.ALIGN_RIGHT|wx.EXPAND, 5 )
		
		now_playing_sizer.Add( playing_buttons_sizer, 1, wx.EXPAND, 5 )
		
		self.progress_slider = wx.Slider( self.now_playing_page, wx.ID_ANY, 50, 0, 100, wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
		now_playing_sizer.Add( self.progress_slider, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.playlist = wx.ListCtrl( self.now_playing_page, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		now_playing_sizer.Add( self.playlist, 0, wx.EXPAND, 5 )
		
		self.now_playing_page.SetSizer( now_playing_sizer )
		self.now_playing_page.Layout()
		now_playing_sizer.Fit( self.now_playing_page )
		self.notebook.AddPage( self.now_playing_page, u"Now playing", True )
		self.page_library = wx.Panel( self.notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.notebook.AddPage( self.page_library, u"Library", False )
		self.page_devices = wx.Panel( self.notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.notebook.AddPage( self.page_devices, u"External devices", False )
		
		main_sizer.Add( self.notebook, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.SetSizer( main_sizer )
		self.Layout()
		main_sizer.Fit( self )
		self.main_menu = wx.MenuBar( 0 )
		self.menu_music = wx.Menu()
		self.item_rescan = wx.MenuItem( self.menu_music, wx.ID_ANY, u"Rescan database", wx.EmptyString, wx.ITEM_NORMAL )
		self.menu_music.AppendItem( self.item_rescan )
		
		self.main_menu.Append( self.menu_music, u"Music" ) 
		
		self.menu_settings = wx.Menu()
		self.item_configure = wx.MenuItem( self.menu_settings, wx.ID_ANY, u"Configure Duck...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menu_settings.AppendItem( self.item_configure )
		
		self.main_menu.Append( self.menu_settings, u"Settings" ) 
		
		self.SetMenuBar( self.main_menu )
		
		self.status_bar = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.previous_button.Bind( wx.EVT_BUTTON, self.do_previous )
		self.play_button.Bind( wx.EVT_BUTTON, self.do_play )
		self.pause_button.Bind( wx.EVT_BUTTON, self.do_pause )
		self.stop_buton.Bind( wx.EVT_BUTTON, self.do_stop )
		self.next_button.Bind( wx.EVT_BUTTON, self.do_next )
	
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
	

