```sh
uv init py-htmlviewer
cd py-htmlviewer
uv venv
uv pip install wxPython
uv pip install pyinstaller
uv run python
```

```sh
pyinstaller --onefile --windowed --add-data "C://sources/ui/venv/Lib/site-packages/wx/WebView2Loader.dll;." py-htmlviewer.py
```