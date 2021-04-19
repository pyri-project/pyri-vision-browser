import js
from RobotRaconteur.Client import *
import importlib_resources
import traceback
import numpy as np
import base64

class NewCameraIntrinsicCalibrationDialog:
    def __init__(self, new_name, core, device_manager):
        self.vue = None
        self.core = core
        self.device_manager = device_manager
        self.new_name = new_name

    def init_vue(self,vue):
        self.vue = vue

    def handle_create(self,*args):
        try:
            camera_local_device_name = self.vue["$data"].camera_selected
            image_sequence_global_name = self.vue["$data"].image_sequence_selected
            calib_target = self.vue["$data"].calibration_target_selected
            self.core.create_task(do_calibration(camera_local_device_name,image_sequence_global_name,calib_target,self.new_name,self.core))
        except:
            traceback.print_exc()

    def handle_hidden(self,*args):
        try:
            l = self.vue["$el"]
            l.parentElement.removeChild(l)
        except:
            traceback.print_exc()
        
        
async def do_show_new_camera_calibration_intrinsic_dialog(new_name: str, variable_type: str, variable_tags: str, core: "PyriWebUIBrowser"):
    try:
        
        core.device_manager.connect_device("vision_camera_calibration")

        dialog_html = importlib_resources.read_text(__package__,"new_calibrate_intrinsic_dialog.html")

        dialog_obj = NewCameraIntrinsicCalibrationDialog(new_name, core, core.device_manager)

        el = js.document.createElement('div')
        el.id = "new_calibrate_intrinsic_dialog_wrapper"
        js.document.getElementById("wrapper").appendChild(el)

        dialog = js.Vue.new(js.python_to_js({
            "el": "#new_calibrate_intrinsic_dialog_wrapper",
            "template": dialog_html,
            "store": core.vuex_store,
            "data":
            {
                "camera_selected": "",
                "camera_select_options": [],
                "image_sequence_selected": "",
                "image_sequence_select_options": [],
                "calibration_target_selected": "",
                "calibration_target_select_options": []
            },
            "methods":
            {
                "handle_create": dialog_obj.handle_create,
                "handle_hidden": dialog_obj.handle_hidden
            }
        }))

        dialog_obj.init_vue(dialog)

        cameras = []
        device_names = dialog["$store"].state.active_device_names
        for d in device_names:
            try:
                implemented_types = dialog["$store"].state.device_infos[d].standard_info.implemented_types
                if "com.robotraconteur.imaging.Camera" in implemented_types:
                    cameras.append({"value": d, "text": d})
            except:
                traceback.print_exc()

        dialog["$data"].camera_select_options = js.python_to_js(cameras)
        if len(cameras) > 0:
            dialog["$data"].camera_selected = cameras[0]["value"]

        db = core.device_manager.get_device_subscription("variable_storage").GetDefaultClient()
        seq_var_names = await db.async_filter_variables("globals","",["image_sequence"],None)

        seq_vars = []
        for v in seq_var_names:
            seq_vars.append({"value": v, "text": v})
        dialog["$data"].image_sequence_select_options = js.python_to_js(seq_vars)
        if len(seq_vars) > 0:
            dialog["$data"].image_sequence_selected = seq_vars[0]["value"]

        cal = [{"value": "chessboard", "text": "chessboard"}]
        dialog["$data"].calibration_target_select_options = js.python_to_js(cal)
        dialog["$data"].calibration_target_selected = "chessboard"

        dialog["$bvModal"].show("new_vision_camera_calibrate_intrinsic")
    except:
        js.alert(f"Calibration failed:\n\n{traceback.format_exc()}")

def show_new_camera_calibration_intrinsic_dialog(new_name: str, variable_type: str, variable_tags: str, core: "PyriWebUIBrowser"):
    core.create_task(do_show_new_camera_calibration_intrinsic_dialog(new_name, variable_type, variable_tags, core))

async def do_calibration(camera_local_device_name, image_sequence_global_name, calib_target, new_name, core):
    try:
        camera_calib = core.device_manager.get_device_subscription("vision_camera_calibration").GetDefaultClient()

        calib_res = await camera_calib.async_calibrate_camera_intrinsic(camera_local_device_name, image_sequence_global_name, calib_target, new_name, None)

    except:
        js.alert(f"Calibration failed:\n\n{traceback.format_exc()}")

    try:
        do_show_new_camera_calibration_intrinsic_dialog2(new_name, calib_res.calibration, calib_res.display_images, core)
    except:
        traceback.print_exc()


def do_show_new_camera_calibration_intrinsic_dialog2(new_name: str, calibration_res, display_images, core: "PyriWebUIBrowser"):
    try:
        dialog2_html = importlib_resources.read_text(__package__,"new_calibrate_intrinsic_dialog2.html")

        el = js.document.createElement('div')
        el.id = "new_calibrate_intrinsic_dialog2_wrapper"
        js.document.getElementById("wrapper").appendChild(el)

        def handle_hidden(*args):
            try:
                el.parentElement.removeChild(el)
            except:
                traceback.print_exc()

        K = np.array_str(calibration_res.K, precision=4, suppress_small=True)
        dist = calibration_res.distortion_info.data
        k1 = f"{dist.k1:4e}"
        k2 = f"{dist.k2:4e}"
        p1 = f"{dist.p1:4e}"
        p2 = f"{dist.p2:4e}"
        k3 = f"{dist.k3:4e}"

        imgs = []
        i=0
        for d in display_images:
            d_encoded = str(base64.b64encode(d.data))[2:-1]
            d2 = {
                "id": i,
                "caption": f"Calibration image result {i+1}",
                "img": "data:image/jpeg;base64," + d_encoded
            }
            del d_encoded
            imgs.append(d2)
            i+=1
            #TODO: check for png?

        dialog = js.Vue.new(js.python_to_js({
            "el": "#new_calibrate_intrinsic_dialog2_wrapper",
            "template": dialog2_html,
            "data":
            {
                "K": K,
                "k1": k1,
                "k2": k2,
                "p1": p1,
                "p2": p2,
                "k3": k3,
                "display_images": imgs
            },
            "methods":
            {
                "handle_hidden": handle_hidden
            }

        }))

        dialog["$bvModal"].show("new_vision_camera_calibrate_intrinsic2")

    except:
        traceback.print_exc()