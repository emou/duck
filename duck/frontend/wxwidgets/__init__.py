from duck.frontend import BaseFrontend

class Frontend(BaseFrontend):
    """
    A frontend, implemented using wxwidgets.
    """

    def run(self):
        """
        Initialize the wxWidgets system, create an application and start the main loop.
        """

        import wx
        from gui.noname import MainWindow

        backend = self.backend
        class DuckWindow(MainWindow):

            def do_previous(self, event):
                backend.previous()

            def do_play(self, event):
                backend.play()

            def do_stop(self, event):
                backend.stop()

            def do_next(self, event):
                backend.next()

        self.application = wx.App()
        self.main_window = DuckWindow(None)
        self.main_window.Show()
        self.application.SetTopWindow(self.main_window)
        return self.application.MainLoop()
