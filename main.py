import os
import wx
import wx.html2

class HtmlViewer(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(1000, 600))
        
        self.splitter = wx.SplitterWindow(self)
        self.panel_left = wx.Panel(self.splitter, style=wx.SUNKEN_BORDER)
        self.panel_right = wx.Panel(self.splitter, style=wx.SUNKEN_BORDER)
        
        self.tree = wx.TreeCtrl(self.panel_left, style=wx.TR_HAS_BUTTONS)
        self.browser = wx.html2.WebView.New(self.panel_right)
        
        self._setup_layout()
        self._populate_tree()
        
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.on_item_expanding, self.tree)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_item_selected, self.tree)
    
    def _setup_layout(self):
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(self.tree, 1, wx.EXPAND)
        self.panel_left.SetSizer(left_sizer)
        
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(self.browser, 1, wx.EXPAND)
        self.panel_right.SetSizer(right_sizer)
        
        self.splitter.SplitVertically(self.panel_left, self.panel_right, 300)
        self.splitter.SetMinimumPaneSize(200)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.splitter, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
    
    def _populate_tree(self):
        root = self.tree.AddRoot("Root")
        self._add_tree_nodes(root, os.getcwd(), lazy_load=True)
        self.tree.Expand(root)
    
    def _add_tree_nodes(self, parent_item, path, lazy_load=False):
        try:
            has_subdirs = False
            for item in sorted(os.listdir(path)):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    dir_item = self.tree.AppendItem(parent_item, item)
                    self.tree.SetItemData(dir_item, full_path)
                    self.tree.AppendItem(dir_item, "...")  # Placeholder for lazy loading
                    has_subdirs = True
                elif item.endswith(".html"):
                    file_item = self.tree.AppendItem(parent_item, item)
                    self.tree.SetItemData(file_item, full_path)
            
            if not has_subdirs and lazy_load:
                self.tree.DeleteChildren(parent_item)
        except PermissionError:
            pass  # Skip folders without permission
    
    def on_item_expanding(self, event):
        item = event.GetItem()
        path = self._get_full_path(item)
        if self.tree.GetChildrenCount(item) == 1:
            first_child = self.tree.GetFirstChild(item)[0]
            if self.tree.GetItemText(first_child) == "...":
                self.tree.Delete(first_child)
                self._add_tree_nodes(item, path)
    
    def on_item_selected(self, event):
        item = event.GetItem()
        path = self._get_full_path(item)
        
        if path and os.path.isfile(path) and path.endswith(".html"):
            self.browser.LoadURL(f"file://{path}")
    
    def _get_full_path(self, item):
        parts = []
        while item.IsOk():
            parts.insert(0, self.tree.GetItemText(item))
            item = self.tree.GetItemParent(item)
        
        return os.path.join(os.getcwd(), *parts[1:])  # Skip the root

if __name__ == "__main__":
    app = wx.App(False)
    frame = HtmlViewer(None, "HTML 파일 탐색기 및 뷰어")
    frame.Show()
    app.MainLoop()
