from pyri.webui_browser.plugins.component import PyriWebUIBrowserComponentPluginFactory
from .camera_list_component import register_vue_components as camera_list_register_vue_components
from .camera_viewer_component import register_vue_components as camera_viewer_register_vue_components

class PyriVisionComponentsWebUIBrowserComponentPluginFactory(PyriWebUIBrowserComponentPluginFactory):
    def get_plugin_name(self) -> str:
        return "pyri-vision-browser"

    def register_components(self) -> None:
        camera_list_register_vue_components()
        camera_viewer_register_vue_components()        

def get_webui_browser_component_factory():
    return PyriVisionComponentsWebUIBrowserComponentPluginFactory()