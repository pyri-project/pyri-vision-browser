from typing import List, Dict, Callable, Any, Tuple
from pyri.webui_browser.plugins.panel import PyriWebUIBrowserPanelInfo, PyriWebUIBrowserPanelPluginFactory
from pyri.webui_browser import PyriWebUIBrowser
from pyri.webui_browser.golden_layout import PyriGoldenLayoutPanelConfig

_panel_infos = {
        
    "camera_list": PyriWebUIBrowserPanelInfo(
        title="Cameras",
        description="List of available cameras",
        panel_type="camera_list",
        panel_category="vision",
        component_type="pyri-camera-list",
        priority=10000
    )
}

_panel_default_configs = {
    "camera_list": PyriGoldenLayoutPanelConfig(
        component_type=_panel_infos["camera_list"].component_type,
        panel_id = "camera_list",
        panel_title = "Cameras",
        closeable= False
    )
}

class PyriVisionPanelsWebUIBrowserPanelPluginFactory(PyriWebUIBrowserPanelPluginFactory):
    def __init__(self):
        super().__init__()

    def get_plugin_name(self) -> str:
        return "pyri-vision-browser"

    def get_panels_infos(self) -> Dict[str,PyriWebUIBrowserPanelInfo]:
        return _panel_infos

    def get_default_panels(self, layout_config: str = "default") -> List[Tuple[PyriWebUIBrowserPanelInfo, "PyriGoldenLayoutPanelConfig"]]:
        if layout_config.lower() == "default":
            return [
                (_panel_infos["camera_list"], _panel_default_configs["camera_list"])
            ]
        else:
            return []

def get_webui_browser_panel_factory():
    return PyriVisionPanelsWebUIBrowserPanelPluginFactory()