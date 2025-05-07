import sys
from pathlib import Path
import wx
import wx.html2

class PyHtmlViewer(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(1000, 600))

        self.splitter = wx.SplitterWindow(self)
        self.panel_left = wx.Panel(self.splitter, style=wx.SUNKEN_BORDER)
        self.panel_right = wx.Panel(self.splitter, style=wx.SUNKEN_BORDER)

        self.tree = wx.TreeCtrl(self.panel_left, style=wx.TR_HAS_BUTTONS)
        self.webview = wx.html2.WebView.New(self.panel_right)

        self._layout()
        self._init()

        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.on_tree_expanding, self.tree)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_sel_changed, self.tree)
        

    def _layout(self):
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(self.tree, 1, wx.EXPAND)
        self.panel_left.SetSizer(left_sizer)

        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(self.webview, 1, wx.EXPAND)
        self.panel_right.SetSizer(right_sizer)

        self.splitter.SplitVertically(self.panel_left, self.panel_right, 300)
        self.splitter.SetMinimumPaneSize(200)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.splitter, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
    

    def _init(self):
        self._init_tree(get_root_path())


    def _init_tree(self, path: Path):
        self.tree.DeleteAllItems()
        if path.name == "":
            root = self.tree.AddRoot(path.resolve().as_posix())
        else:
            root = self.tree.AddRoot(path.name)
        self.tree.SetItemData(root, path)
        self.tree.SetItemHasChildren(root, True)

        self._add_tree_nodes(root, path)
        self.tree.Expand(root)
    

    def _add_tree_nodes(self, parent_item, parent_path: Path):
        for path in parent_path.iterdir():
            try:
                if path.is_dir():
                    dir_item = self.tree.AppendItem(parent_item, path.name)
                    self.tree.SetItemData(dir_item, path)
                    self.tree.SetItemHasChildren(dir_item, has_children(path))
                elif path.is_file() and path.suffix.lower() == ".html":
                    file_item = self.tree.AppendItem(parent_item, path.name)
                    self.tree.SetItemData(file_item, path)
            except PermissionError:
                pass


    def on_tree_expanding(self, event):
        item = event.GetItem()
        self.tree.DeleteChildren(item)
        path = self.tree.GetItemData(item)
        if path.is_dir():
            self._add_tree_nodes(item, path)


    def on_tree_sel_changed(self, event):
        item = event.GetItem()
        path = self.tree.GetItemData(item)
        if path.is_file() and path.suffix.lower() == ".html":
            self.webview.LoadURL(path.as_uri())


def main():
    app = wx.App(False)
    frame = PyHtmlViewer(None, "Html Viewer")
    frame.Show()
    app.MainLoop()


def get_root_path() -> Path:
    root_path = Path(".")
    if getattr(sys, "frozen", False):
        root_path = Path(sys.executable).parent
    else:
        root_path = Path(__file__).resolve().parent
    if len(sys.argv) > 1:
        arg_path = Path(sys.argv[1])
        if arg_path.is_dir():
            root_path = arg_path
        elif arg_path.is_file():
            root_path = arg_path.parent
    return root_path


def has_children(path: Path) -> bool:
    return path.exists() and any(path.iterdir())


if __name__ == "__main__":
    main()
