import js
from RobotRaconteur.Client import *
import importlib_resources
import traceback
import numpy as np
import base64
from RobotRaconteurCompanion.Util.GeometryUtil import GeometryUtil
from pyri.webui_browser import util

class NewCameraExtrinsicCalibrationDialog:
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
            intrins_global_name = self.vue["$data"].camera_intrinsic_selected
            image_global_name = self.vue["$data"].image_selected
            calib_target = self.vue["$data"].calibration_target_selected
            self.core.create_task(do_calibration(camera_local_device_name,intrins_global_name,image_global_name,calib_target,self.new_name,self.core))
        except:
            traceback.print_exc()

    def handle_hidden(self,*args):
        try:
            l = self.vue["$el"]
            l.parentElement.removeChild(l)
        except:
            traceback.print_exc()
        
        
async def do_show_new_camera_calibration_extrinsic_dialog(new_name: str, variable_type: str, variable_tags: str, core: "PyriWebUIBrowser"):
    try:
        
        core.device_manager.connect_device("vision_camera_calibration")

        dialog_html = importlib_resources.read_text(__package__,"new_calibrate_extrinsic_dialog.html")

        dialog_obj = NewCameraExtrinsicCalibrationDialog(new_name, core, core.device_manager)

        el = js.document.createElement('div')
        el.id = "new_calibrate_extrinsic_dialog_wrapper"
        js.document.getElementById("wrapper").appendChild(el)

        dialog = js.Vue.new(js.python_to_js({
            "el": "#new_calibrate_extrinsic_dialog_wrapper",
            "template": dialog_html,
            "data":
            {
                "camera_selected": "",
                "camera_select_options": [],
                "camera_intrinsic_selected": "",
                "camera_intrinsic_select_options": [],
                "image_selected": "",
                "image_select_options": [],
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
        camera_names = util.get_devices_with_type(core, "com.robotraconteur.imaging.Camera")
        cameras = util.device_names_to_dropdown_options(camera_names)

        dialog["$data"].camera_select_options = js.python_to_js(cameras)
        if len(cameras) > 0:
            dialog["$data"].camera_selected = cameras[0]["value"]

        db = core.device_manager.get_device_subscription("variable_storage").GetDefaultClient()
        img_var_names = await db.async_filter_variables("globals","",["image"],None)

        img_vars = []
        for v in img_var_names:
            img_vars.append({"value": v, "text": v})
        dialog["$data"].image_select_options = js.python_to_js(img_vars)
        if len(img_vars) > 0:
            dialog["$data"].image_selected = img_vars[0]["value"]

        intrins_var_names = await db.async_filter_variables("globals","",["camera_calibration_intrinsic"],None)
        intrins_vars = []
        for v in intrins_var_names:
            intrins_vars.append({"value": v, "text": v})
        dialog["$data"].camera_intrinsic_select_options = js.python_to_js(intrins_vars)
        if len(intrins_vars) > 0:
            dialog["$data"].camera_intrinsic_selected = intrins_vars[0]["value"]

        cal = [{"value": "chessboard", "text": "chessboard"}]
        dialog["$data"].calibration_target_select_options = js.python_to_js(cal)
        dialog["$data"].calibration_target_selected = "chessboard"

        dialog["$bvModal"].show("new_vision_camera_calibrate_extrinsic")
    except:
        js.alert(f"Calibration failed:\n\n{traceback.format_exc()}")

def show_new_camera_calibration_extrinsic_dialog(new_name: str, variable_type: str, variable_tags: str, core: "PyriWebUIBrowser"):
    core.create_task(do_show_new_camera_calibration_extrinsic_dialog(new_name, variable_type, variable_tags, core))

async def do_calibration(camera_local_device_name, intrins_calib_global_name, image_global_name, calib_target, new_name, core):
    try:
        camera_calib = core.device_manager.get_device_subscription("vision_camera_calibration").GetDefaultClient()

        calib_res = await camera_calib.async_calibrate_camera_extrinsic(camera_local_device_name, intrins_calib_global_name, image_global_name, calib_target, new_name, None)

    except:
        js.alert(f"Calibration failed:\n\n{traceback.format_exc()}")
        return

    try:
        do_show_new_camera_calibration_extrinsic_dialog2(new_name, calib_res.camera_pose, calib_res.display_image, core)
    except:
        traceback.print_exc()


def do_show_new_camera_calibration_extrinsic_dialog2(new_name: str, camera_pose, display_image, core: "PyriWebUIBrowser"):
    try:
        camera_calib = core.device_manager.get_device_subscription("vision_camera_calibration").GetDefaultClient()

        dialog2_html = importlib_resources.read_text(__package__,"new_calibrate_extrinsic_dialog2.html")

        el = js.document.createElement('div')
        el.id = "new_calibrate_extrinsic_dialog2_wrapper"
        js.document.getElementById("wrapper").appendChild(el)

        def handle_hidden(*args):
            try:
                el.parentElement.removeChild(el)
            except:
                traceback.print_exc()
        geom_util = GeometryUtil(client_obj=camera_calib)
        xyz, rpy1, _, _ = geom_util.named_pose_to_xyz_rpy(camera_pose.pose)
        rpy = np.rad2deg(rpy1)
        
        x = f"{xyz[0]:4e}"
        y = f"{xyz[1]:4e}"
        z = f"{xyz[2]:4e}"
        r_r = f"{rpy[0]:4e}"
        r_p = f"{rpy[1]:4e}"
        r_y = f"{rpy[2]:4e}"

        i=0
        
        d_encoded = str(base64.b64encode(display_image.data))[2:-1]
        disp_img_src = "data:image/jpeg;base64," + d_encoded
        # TODO: check for png?
        
        dialog = js.Vue.new(js.python_to_js({
            "el": "#new_calibrate_extrinsic_dialog2_wrapper",
            "template": dialog2_html,
            "data":
            {
                "x": x,
                "y": y,
                "z": z,
                "r_r": r_r,
                "r_p": r_p,
                "r_y": r_y,
                "disp_img": disp_img_src
            },
            "methods":
            {
                "handle_hidden": handle_hidden
            }

        }))

        dialog["$bvModal"].show("new_vision_camera_calibrate_extrinsic2")
        
    except:
        traceback.print_exc()