import wx

from duck.frontend.wxwidgets.mixins import ListCtrlAutoRelativeWidthMixin

class NiceListCtrl(wx.ListCtrl, ListCtrlAutoRelativeWidthMixin):

    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        ListCtrlAutoRelativeWidthMixin.__init__(self)
