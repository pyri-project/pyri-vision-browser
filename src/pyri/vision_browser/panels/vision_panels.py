from typing import List, Dict, Callable, Any
from pyri.webui_browser.plugins.panel import PyriWebUIBrowserPanelInfo, PyriWebUIBrowserPanelPluginFactory, PyriWebUIBrowserPanelBase
from pyri.webui_browser import PyriWebUIBrowser
from .vision_panel import add_vision_panel

_panel_infos = {
        
    "vision": PyriWebUIBrowserPanelInfo(
        title="Vision",
        panel_type="vision",
        priority=5000
    )
}

class PyriVisionPanelsWebUIBrowserPanelPluginFactory(PyriWebUIBrowserPanelPluginFactory):
    def __init__(self):
        super().__init__()

    def get_plugin_name(self) -> str:
        return "pyri-vision-browser"

    def get_panels_infos(self) -> Dict[str,PyriWebUIBrowserPanelInfo]:
        return _panel_infos

    async def add_panel(self, panel_type: str, core: PyriWebUIBrowser, parent_element: Any) -> PyriWebUIBrowserPanelBase:
        if panel_type == "vision":
            return await add_vision_panel(panel_type, core, parent_element)
        assert False, f"Unknown panel_type \"{panel_type}\" specified"

def get_webui_browser_panel_factory():
    return PyriVisionPanelsWebUIBrowserPanelPluginFactory()