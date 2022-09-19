from typing import List, Dict, Callable, Any
import importlib_resources
import js
import traceback
from RobotRaconteur.Client import *
from pyri.webui_browser import util
from pyri.webui_browser.util import to_js2
from pyri.webui_browser.pyri_vue import PyriVue, VueComponent, vue_register_component, vue_data, \
    vue_method, vue_prop, vue_computed, vue_watch

import base64

@VueComponent
class PyriCameraViewerComponent(PyriVue):

    vue_template = importlib_resources.read_text(__package__,"camera_viewer_component.html")

    camera_local_device_name = vue_prop()

    component_info = vue_prop()

    capturing_sequence = vue_data(False)
    captured_sequence_global_name = vue_data("")
    captured_sequence_count = vue_data(0)
    save_system_state_checked = vue_data(True)

    def __init__(self):
        super().__init__()
        self._camera_local_name = None        
        self.viewer_connected = False
        self._destroyed = False

    def core_ready(self):
        super().core_ready()

        self.viewer_img = self.refs.camera_viewer_img

        if self.camera_local_device_name:
            self._camera_local_name = self.camera_local_device_name
        else:
            self._camera_local_name = self.component_info.camera_local_device_name

        self.core.create_task(self._run_viewer())

    def before_destroy(self):
        super().before_destroy()
        self._destroyed = True

    async def _run_viewer(self):

        viewer_obj = None
        img = None
        try:
            while not self._destroyed:
                try:
                    if viewer_obj is None:
                        if not self.viewer_connected:
                            try:
                                self.core.device_manager.connect_device("vision_camera_viewer")
                                self.viewer_connected = True
                            except:
                                pass                            
                        viewer_service = self.core.device_manager.get_device_subscription("vision_camera_viewer").GetDefaultClient()
                        viewer_obj = await viewer_service.async_get_camera_viewer(self._camera_local_name,None)
                    img = await viewer_obj.async_capture_frame_preview(None)
                except:
                    traceback.print_exc()
                    viewer_obj = None
                else:                   
                    encoded = str(base64.b64encode(img.data))[2:-1]
                    self.viewer_img.src = "data:image/jpeg;base64," + encoded

                img = None
                
                await RRN.AsyncSleep(0.001,None)
        except:
            traceback.print_exc()
    
    @vue_method
    async def save_to_globals(self, *args):
        try:
            global_name = js.prompt("global name")
            if global_name is None or global_name == "":
                return
            save_state = self.save_system_state_checked
            viewer_service = self.core.device_manager.get_device_subscription("vision_camera_viewer").GetDefaultClient()
            viewer_obj = await viewer_service.async_get_camera_viewer(self._camera_local_name,None)
            await viewer_obj.async_save_to_globals(global_name, save_state, None)

            js.alert(f"Image \"{global_name}\" saved")
        except:
            js.alert(f"Save image failed:\n\n{traceback.format_exc()}")
            traceback.print_exc()

    @vue_method
    async def save_sequence_to_globals(self, *args):
        try:
            global_name = js.prompt("global name")
            if global_name is None or global_name == "":
                return
            self.capturing_sequence=True
            self.captured_sequence_count=0
            self.captured_sequence_global_name=global_name

            save_state = self.save_system_state_checked
            viewer_service = self.core.device_manager.get_device_subscription("vision_camera_viewer").GetDefaultClient()
            viewer_obj = await viewer_service.async_get_camera_viewer(self._camera_local_name,None)
            self._sequence_gen = await viewer_obj.async_save_sequence_to_globals(global_name, save_state, None)

        except:
            self._sequence_gen = None
            js.alert(f"Save image sequence failed:\n\n{traceback.format_exc()}")
            traceback.print_exc()


    @vue_method
    async def sequence_capture_next(self, *args):
        self.captured_sequence_count+=1
        try:            
            # TODO: AsyncNext should only have one argument
            await self._sequence_gen.AsyncNext(None,None)
        except:
            self._sequence_gen = None
            js.alert(f"Save image sequence failed:\n\n{traceback.format_exc()}")
            traceback.print_exc()

    @vue_method
    async def sequence_capture_done(self, *args):
        self.capturing_sequence=False
        self.captured_sequence_count=0
        self.captured_sequence_global_name=""
        try:            
            await self._sequence_gen.AsyncClose(None)
            self._sequence_gen = None
        except:
            self._sequence_gen = None
            js.alert(f"Save image sequence failed:\n\n{traceback.format_exc()}")
            traceback.print_exc()

    @vue_method
    async def sequence_capture_cancel(self, *evt):
        self.capturing_sequence=False
        self.captured_sequence_count=0
        self.captured_sequence_global_name=""
        try:            
            await self._sequence_gen.AsyncAbort(None)
            self._sequence_gen = None
        except:
            self._sequence_gen = None
            js.alert(f"Save image sequence failed:\n\n{traceback.format_exc()}")
            traceback.print_exc()

def register_vue_components():
    vue_register_component('pyri-camera-viewer', PyriCameraViewerComponent)

async def open_camera_viewer_panel(core, camera_local_device_name, parent_panel_id = "root"):

    from pyri.webui_browser.golden_layout import PyriGoldenLayoutPanelConfig

    viewer_panel_config = PyriGoldenLayoutPanelConfig(
        component_type= "pyri-camera-viewer",
        panel_id = f"camera_viewer_{camera_local_device_name}",
        panel_title = camera_local_device_name,
        closeable=True, 
        component_info = {
            "camera_local_device_name": camera_local_device_name
        },
    )

    await core.layout.add_panel(viewer_panel_config, parent_panel_id)
