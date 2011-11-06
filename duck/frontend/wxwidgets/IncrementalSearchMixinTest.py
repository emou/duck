import unittest
import wx

from duck.frontend.wxwidgets.ducklist import ListCtrlIncrementalSearchMixin, Column

class MyAutoCompleteCtrl(ListCtrlIncrementalSearchMixin, wx.ListCtrl):
    DEFAULT_SEARCH_COLUMNS = [0]
    DATA=[('Alice',), ('Bob',), ('Ben',), ('Chuck',)]

    def __init__(self, *args, **kwargs):
        search_columns = kwargs.pop(
            'search_columns',
            self.DEFAULT_SEARCH_COLUMNS,
        )
        columns = kwargs.pop('columns', Column(name='Name'))
        wx.ListCtrl.__init__(self, *args, **kwargs)
        ListCtrlIncrementalSearchMixin.__init__(self,
                                                search_field=wx.TextCtrl(self),
                                                columns=columns,
                                                search_columns=search_columns)
        self.load_data(self.DATA)

class IncrementalSearchMixinInitializeTest(unittest.TestCase):
        def setUp(self):
            self.app = wx.App()
            self.parent_frame = wx.Frame(None)

        def test_exception_on_non_virtual_init(self):
            class MyAutoCompleteNoColumns(wx.ListCtrl,
                                          ListCtrlIncrementalSearchMixin):
                def __init__(self, *args, **kwargs):
                    wx.ListCtrl.__init__(self, *args, **kwargs)
                    ListCtrlIncrementalSearchMixin.__init__(
                        self,
                        search_field=wx.TextCtrl(self),
                        search_columns=[0],
                        columns=(Column('Name', None),),
                    )
            self.assertRaises(ValueError,
                              MyAutoCompleteNoColumns, self.parent_frame)

        def test_exception_on_no_columns(self):
            self.assertRaises(ValueError,
                              MyAutoCompleteCtrl,
                              self.parent_frame,
                              style=wx.LC_REPORT,
                              search_columns=['a'])

class IncrementalSearchTest(unittest.TestCase):

    def setUp(self):
        self.app = wx.App()
        self.parent_frame = wx.Frame(None)
        self.auto_completer = MyAutoCompleteCtrl(
            self.parent_frame,
            style=wx.LC_REPORT | wx.LC_VIRTUAL
        )
    
    def test_filter(self):
        self.assertEquals(self.auto_completer.GetItemCount(),
                          len(MyAutoCompleteCtrl.DATA))

        char_event = wx.CommandEvent(wx.wxEVT_COMMAND_TEXT_UPDATED)
        char_event.SetString('a')
        self.auto_completer.search_field.ProcessEvent(char_event)

        self.assertEquals('a',
                          self.auto_completer.search_term)
        # Only Alice matches the search term 'a'.
        self.assertEquals(len(self.auto_completer.data),
                          len(MyAutoCompleteCtrl.DATA))
        self.assertEquals(1, self.auto_completer.GetItemCount())
        self.assertEquals(1, len(self.auto_completer.filtered))
        self.assertEquals(
            'Alice',
            self.auto_completer.data[self.auto_completer.filtered[0]][0]
        )
        self.assertEquals(
            'Alice',
            self.auto_completer.GetItemText(0,0),
        )
        # "Assert not raises"
        self.auto_completer.GetItemFont(0)
        # Cant get item font of 'Bob' because it's filtered out right now.
        self.assertRaises(ValueError, self.auto_completer.GetItemFont, 1)

        # ESC cancels search.
        char_event_end = wx.KeyEvent(wx.wxEVT_CHAR)
        char_event_end.m_keyCode = wx.WXK_ESCAPE
        self.auto_completer.search_field.ProcessEvent(char_event_end)

        self.assertEquals(self.auto_completer.GetItemCount(),
                          len(MyAutoCompleteCtrl.DATA))

if __name__ == '__main__':
    unittest.main()
