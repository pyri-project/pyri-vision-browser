import js
from RobotRaconteur.Client import *
import importlib_resources
import traceback
import numpy as np
import base64
from RobotRaconteurCompanion.Util.GeometryUtil import GeometryUtil
from pyri.webui_browser import util

class NewRobotOriginCalibrationDialog:
    def __init__(self, new_name, core, device_manager):
        self.vue = None
        self.core = core
        self.device_manager = device_manager
        self.new_name = new_name

    def init_vue(self,vue):
        self.vue = vue

    def handle_create(self,*args):
        try:
            robot_local_device_name = self.vue["$data"].robot_selected
            intrinsic_calib = self.vue["$data"].camera_intrinsic_selected
            extrinsic_calib = self.vue["$data"].camera_extrinsic_selected
            image_sequence_global_name = self.vue["$data"].image_sequence_selected
            aruco_dict = self.vue["$data"].aruco_dict_selected
            aruco_tag_id = int(self.vue["$data"].aruco_tag_id)
            aruco_tag_size = float(self.vue["$data"].aruco_tag_size)
            xyz = np.zeros((3,),dtype=np.float64)
            rpy = np.zeros((3,),dtype=np.float64)
            xyz[0] = float(self.vue["$data"].marker_pose_x)
            xyz[1] = float(self.vue["$data"].marker_pose_y)
            xyz[2] = float(self.vue["$data"].marker_pose_z)
            rpy[0] = float(self.vue["$data"].marker_pose_r_r)
            rpy[1] = float(self.vue["$data"].marker_pose_r_p)
            rpy[2] = float(self.vue["$data"].marker_pose_r_y)

            rpy = np.deg2rad(rpy)

            robot_calib = self.core.device_manager.get_device_subscription("vision_robot_calibration").GetDefaultClient()
            geom_util = GeometryUtil(client_obj = robot_calib)
            marker_pose = geom_util.xyz_rpy_to_pose(xyz, rpy)
            
            self.core.create_task(do_calibration(robot_local_device_name,intrinsic_calib,extrinsic_calib,\
                image_sequence_global_name,aruco_dict,aruco_tag_id, aruco_tag_size, marker_pose, self.new_name,self.core))
        except:
            traceback.print_exc()

    def handle_hidden(self,*args):
        try:
            l = self.vue["$el"]
            l.parentElement.removeChild(l)
        except:
            traceback.print_exc()
        
        
async def do_show_new_robot_origin_calibration_dialog(new_name: str, variable_type: str, variable_tags: str, core: "PyriWebUIBrowser"):
    try:
        
        core.device_manager.connect_device("vision_robot_calibration")

        dialog_html = importlib_resources.read_text(__package__,"new_calibrate_robot_origin_dialog.html")

        dialog_obj = NewRobotOriginCalibrationDialog(new_name, core, core.device_manager)

        el = js.document.createElement('div')
        el.id = "new_calibrate_robot_origin_dialog_wrapper"
        js.document.getElementById("wrapper").appendChild(el)

        dialog = js.Vue.new(js.python_to_js({
            "el": "#new_calibrate_robot_origin_dialog_wrapper",
            "template": dialog_html,
            "data":
            {
                "robot_selected": "",
                "robot_select_options": [],
                "camera_intrinsic_selected": "",
                "camera_intrinsic_select_options": [],
                "camera_extrinsic_selected": "",
                "camera_extrinsic_select_options": [],
                "image_sequence_selected": "",
                "image_sequence_select_options": [],
                "aruco_dict_selected": "",
                "aruco_dict_select_options": [],
                "aruco_tag_id": "120",
                "aruco_tag_size": "0.06",
                "marker_pose_x": "0",
                "marker_pose_y": "0",
                "marker_pose_z": "0",
                "marker_pose_r_r": "0",
                "marker_pose_r_p": "0",
                "marker_pose_r_y": "0",
                
            },
            "methods":
            {
                "handle_create": dialog_obj.handle_create,
                "handle_hidden": dialog_obj.handle_hidden
            }
        }))

        dialog_obj.init_vue(dialog)

        robots = []
        robot_names = util.get_devices_with_type(core, "com.robotraconteur.robotics.robot.Robot")
        robots = util.device_names_to_dropdown_options(robot_names)
        
        dialog["$data"].robot_select_options = js.python_to_js(robots)
        if len(robots) > 0:
            dialog["$data"].robot_selected = robots[0]["value"]

        db = core.device_manager.get_device_subscription("variable_storage").GetDefaultClient()

        intrins_var_names = await db.async_filter_variables("globals","",["camera_calibration_intrinsic"],None)
        intrins_vars = []
        for v in intrins_var_names:
            intrins_vars.append({"value": v, "text": v})
        dialog["$data"].camera_intrinsic_select_options = js.python_to_js(intrins_vars)
        if len(intrins_vars) > 0:
            dialog["$data"].camera_intrinsic_selected = intrins_vars[0]["value"]

        extrins_var_names = await db.async_filter_variables("globals","",["camera_calibration_extrinsic"],None)
        extrins_vars = []
        for v in extrins_var_names:
            extrins_vars.append({"value": v, "text": v})
        dialog["$data"].camera_extrinsic_select_options = js.python_to_js(extrins_vars)
        if len(extrins_vars) > 0:
            dialog["$data"].camera_extrinsic_selected = extrins_vars[0]["value"]

        
        seq_var_names = await db.async_filter_variables("globals","",["image_sequence"],None)

        seq_vars = []
        for v in seq_var_names:
            seq_vars.append({"value": v, "text": v})
        dialog["$data"].image_sequence_select_options = js.python_to_js(seq_vars)
        if len(seq_vars) > 0:
            dialog["$data"].image_sequence_selected = seq_vars[0]["value"]

        aruco_dicts = ['DICT_4X4_100', 'DICT_4X4_1000', 'DICT_4X4_250', \
            'DICT_4X4_50', 'DICT_5X5_100', 'DICT_5X5_1000', 'DICT_5X5_250', \
            'DICT_5X5_50', 'DICT_6X6_100', 'DICT_6X6_1000', 'DICT_6X6_250', \
            'DICT_6X6_50', 'DICT_7X7_100', 'DICT_7X7_1000', 'DICT_7X7_250', \
            'DICT_7X7_50', 'DICT_APRILTAG_16H5', 'DICT_APRILTAG_16h5', 'DICT_APRILTAG_25H9', \
            'DICT_APRILTAG_25h9', 'DICT_APRILTAG_36H10', 'DICT_APRILTAG_36H11', 'DICT_APRILTAG_36h10', \
            'DICT_APRILTAG_36h11', 'DICT_ARUCO_ORIGINAL']

        aruco_opts = [{"value": v,"text": v} for v in aruco_dicts]

        dialog["$data"].aruco_dict_select_options = js.python_to_js(aruco_opts)
        dialog["$data"].aruco_dict_selected = 'DICT_6X6_250'
        
        dialog["$bvModal"].show("new_vision_camera_calibrate_robot_origin")
    except:
        js.alert(f"Calibration failed:\n\n{traceback.format_exc()}")

def show_new_robot_origin_calibration_dialog(new_name: str, variable_type: str, variable_tags: str, core: "PyriWebUIBrowser"):
    core.create_task(do_show_new_robot_origin_calibration_dialog(new_name, variable_type, variable_tags, core))

async def do_calibration(robot_local_device_name, intrinsic_calib, extrinsic_calib, \
    image_sequence_global_name, aruco_dict, aruco_tag_id, aruco_tag_size, marker_pose, new_name, core):

    try:
        robot_calib = core.device_manager.get_device_subscription("vision_robot_calibration").GetDefaultClient()

        calib_res = await robot_calib.async_calibrate_robot_origin(robot_local_device_name, intrinsic_calib, \
            extrinsic_calib, image_sequence_global_name, aruco_dict, aruco_tag_id, aruco_tag_size, \
            marker_pose, new_name, None)

    except:
        js.alert(f"Calibration failed:\n\n{traceback.format_exc()}")
        return

    try:
        do_show_new_robot_origin_calibration_dialog2(new_name, calib_res.robot_pose, calib_res.display_images, core)
    except:
        traceback.print_exc()


def do_show_new_robot_origin_calibration_dialog2(new_name: str, robot_pose, display_images, core: "PyriWebUIBrowser"):
    try:
        dialog2_html = importlib_resources.read_text(__package__,"new_calibrate_robot_origin_dialog2.html")

        robot_calib = core.device_manager.get_device_subscription("vision_robot_calibration").GetDefaultClient()
        geom_util = GeometryUtil(client_obj = robot_calib)
        marker_xyz, marker_rpy, _, _ = geom_util.named_pose_to_xyz_rpy(robot_pose.pose)

        el = js.document.createElement('div')
        el.id = "new_calibrate_robot_origin_dialog2_wrapper"
        js.document.getElementById("wrapper").appendChild(el)

        def handle_hidden(*args):
            try:
                el.parentElement.removeChild(el)
            except:
                traceback.print_exc()

        x = f"{marker_xyz[0]:4e}"
        y = f"{marker_xyz[1]:4e}"
        z = f"{marker_xyz[2]:4e}"
        r_r = f"{marker_rpy[0]:4e}"
        r_p = f"{marker_rpy[1]:4e}"
        r_y = f"{marker_rpy[2]:4e}"
        

        imgs = []
        i=0
        for d in display_images:
            d_encoded = str(base64.b64encode(d.data))[2:-1]
            d2 = {
                "id": i,
                "caption": f"Calibration result {i+1}",
                "img": "data:image/jpeg;base64," + d_encoded
            }
            del d_encoded
            imgs.append(d2)
            i+=1
            #TODO: check for png?

        dialog = js.Vue.new(js.python_to_js({
            "el": "#new_calibrate_robot_origin_dialog2_wrapper",
            "template": dialog2_html,
            "data":
            {
                "x": x,
                "y": y,
                "z": z,
                "r_r": r_r,
                "r_p": r_p,
                "r_y": r_y,
                "display_images": imgs
            },
            "methods":
            {
                "handle_hidden": handle_hidden
            }

        }))

        dialog["$bvModal"].show("new_vision_camera_calibrate_robot_origin2")

    except:
        traceback.print_exc()