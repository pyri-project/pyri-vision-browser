from typing import List, Dict, Callable, Any
import importlib_resources
import js
import traceback
from RobotRaconteur.Client import *
from pyri.webui_browser import util
from pyri.webui_browser.util import to_js2
from pyri.webui_browser.pyri_vue import PyriVue, VueComponent, vue_register_component, vue_data, \
    vue_method, vue_prop, vue_computed, vue_watch

@VueComponent
class PyriCameraListComponent(PyriVue):

    vue_template = importlib_resources.read_text(__package__,"camera_list_component.html")

    vue_components = {
            "BootstrapTable": js.window.BootstrapTable
        }

    cameras = vue_data(lambda: [])
    cameras_columns = vue_data(lambda vue:
        [
            {
                "field": "local_device_name",
                "title": "Camera Device Name"
            },
            {
                "field": "actions",
                "title": "Actions",
                "searchable": False,
                "formatter": lambda a,b,c,d: """
                                            <a class="camera_list_open" title="Open Preview" @click="camera_open(c.local_device_name)"><i class="fas fa-2x fa-folder-open"></i></a>&nbsp;
                                            <a class="camera_list_info" title="Camera Info" @click="camera_info(c.local_device_name)"><i class="fas fa-2x fa-info-circle"></i></a>&nbsp;
                                            """
                                            #<a class="camera_lest_settings" title="Camera Settings" @click="camera_settings(c.local_device_name)"><i class="fas fa-2x fa-cog"></i></a>
                                                ,
                "events": {
                    "click .camera_list_open": js.Function.new("vue_this", "return (function (e, value, row, d) { vue_this.camera_open(row.local_device_name); })")(vue),
                    "click .camera_list_info": js.Function.new("vue_this", "return (function (e, value, row, d) { vue_this.camera_info(row.local_device_name); })")(vue),
                }
            },                               
        ]
    )
    camera_list_options = vue_data(lambda:
        {
            "search": True,
            "showColumns": False,
            "showToggle": True,
            "search": True,
            "showSearchClearButton": True,
            "showRefresh": False,
            "cardView": True,
            "toolbar": "#camera_list_toolbar"
        }
    )

    def __init__(self):
        super().__init__()

    @vue_method
    async def camera_open(self, local_device_name):
        from .camera_viewer_component import open_camera_viewer_panel
        await open_camera_viewer_panel(self.core, local_device_name)

    @vue_method
    def camera_info(self, local_device_name):
        pass

    @vue_method
    def camera_settings(self, local_device_name):
        pass
    
    @vue_method
    def refresh_cameras_table(self,*args):
        try:
            cameras = util.get_devices_with_type(self.core,"com.robotraconteur.imaging.Camera")
                        
            getattr(self.vue,"$data").cameras = to_js2([{"local_device_name": d} for d in cameras])
        except:
            traceback.print_exc()

def register_vue_components():
    vue_register_component('pyri-camera-list', PyriCameraListComponent)