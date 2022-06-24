import js
from RobotRaconteur.Client import *
import importlib_resources
import traceback
import numpy as np
import base64
from RobotRaconteurCompanion.Util.GeometryUtil import GeometryUtil
from pyri.webui_browser.util import to_js2

class NewImageRoiDialog:
    def __init__(self, new_name, core, device_manager):
        self.vue = None
        self.core = core
        self.device_manager = device_manager
        self.new_name = new_name
        self.cropper = None

    def init_vue(self, vue):
        self.vue = vue

    async def do_handle_create(self, x,y,w,h,theta):
        try:
            var_storage = self.device_manager.get_device_subscription("variable_storage").GetDefaultClient()
            b = RRN.NewStructure("com.robotraconteur.geometry.BoundingBox2D", var_storage)
            center = RRN.NewStructure("com.robotraconteur.geometry.NamedPose2D", var_storage)
            pose2d_dtype = RRN.GetNamedArrayDType("com.robotraconteur.geometry.Pose2D", var_storage)
            size2d_dtype = RRN.GetNamedArrayDType("com.robotraconteur.geometry.Size2D", var_storage)
            center.pose = np.zeros((1,),dtype=pose2d_dtype)
            center.pose[0]["position"]["x"] = x
            center.pose[0]["position"]["y"] = y
            center.pose[0]["orientation"] = theta
            b.center = center
            size = np.zeros((1,),dtype=size2d_dtype)
            size[0]["width"] = w
            size[0]["height"] = h
            b.size = size

            var_consts = RRN.GetConstants('tech.pyri.variable_storage', var_storage)
            variable_persistence = var_consts["VariablePersistence"]
            variable_protection_level = var_consts["VariableProtectionLevel"]

            await var_storage.async_add_variable2("globals", self.new_name ,"com.robotraconteur.geometry.BoundingBox2D", \
                RR.VarValue(b,"com.robotraconteur.geometry.BoundingBox2D"), ["image_roi"], {}, \
                variable_persistence["const"], None, variable_protection_level["read_write"], \
                [], "Image region of interest", False, None)

        except:
            js.alert(f"Save image roi failed:\n\n{traceback.format_exc()}")
        

    def handle_create(self, *args):
        try:
            crop_data = self.cropper.getData()
            
            cropper_x = float(crop_data.x)
            cropper_y = float(crop_data.y)
            cropper_w = float(crop_data.width)
            cropper_h = float(crop_data.height)
            cropper_r = np.deg2rad(float(crop_data.rotate))
            
            img_data = self.cropper.getImageData()
            
            cropper_img_w = float(img_data.naturalWidth)
            cropper_img_h = float(img_data.naturalHeight)

            c = np.cos(cropper_r)
            s = np.sin(cropper_r)

            corner1 = np.array([c*cropper_img_w, s*cropper_img_w])
            corner3 = np.array([-s*cropper_img_h,c*cropper_img_h])
            corner2 = corner1 + corner3

            img_x_min = np.min([0.,corner1[0],corner2[0],corner3[0]])
            #img_x_max = np.max([0.,corner1[0],corner2[0],corner3[0]])
            img_y_min = np.min([0.,corner1[1],corner2[1],corner3[1]])
            #img_y_max = np.max([0.,corner1[1],corner2[1],corner3[1]])

            center_x_unrotated1 = cropper_x + img_x_min + cropper_w/2.
            center_y_unrotated1 = cropper_y + img_y_min + cropper_h/2.

            R = np.array([[c,s],[-s,c]])
            center_unrotated1 = np.array([center_x_unrotated1,center_y_unrotated1],dtype=np.float64)
            center = R@center_unrotated1

            x = center[0]
            y = center[1]
            w = cropper_w
            h = cropper_h
            theta = -cropper_r
            #print(f"x: {x}, y: {y}, w: {w}, h: {h}, theta: {theta}")
            self.core.create_task(self.do_handle_create(x,y,w,h,theta))
        except:
            js.alert(f"Save image roi failed:\n\n{traceback.format_exc()}")

    def handle_hidden(self, *args):
        try:
            l = getattr(self.vue,"$el")
            l.parentElement.removeChild(l)
        except:
            traceback.print_exc()

    def image_select_changed(self, image_name):
        self.core.create_task(self.set_image(image_name))
        

    def image_reset(self, *args):
        if self.cropper is not None:
            self.cropper.reset()

    def image_rot_m5(self, *args):
        if self.cropper is not None:
            self.cropper.rotate(-5)

    def image_rot_p5(self, *args):
        if self.cropper is not None:
            self.cropper.rotate(5)

    async def set_image(self, image_global_name):
        
        try:
            db = self.device_manager.get_device_subscription("variable_storage").GetDefaultClient()
            img1 = await db.async_getf_variable_value("globals", image_global_name, None)
            img = img1.data
            d_encoded = str(base64.b64encode(img.data))[2:-1]
            if np.array_equal(img.data[0:3], np.array([0xFF, 0xD8, 0xFF], dtype=np.uint8)):
                img_src = "data:image/jpeg;base64," + d_encoded
            elif np.array_equal(img.data[0:3], np.array([0x89, 0x50, 0x4E], dtype=np.uint8)):
                img_src = "data:image/png;base64," + d_encoded
            else:
                js.alert("Invalid image magic")
                raise Exception("Invalid image magic")
            if self.cropper is None:
                img_el = js.document.getElementById("roi_select_image")
                img_el.src = img_src
                self.cropper = js.Cropper.new(img_el, to_js2({"viewMode":2}))
            else:
                self.cropper.reset()
                self.cropper.replace(img_src)
        except:
            traceback.print_exc()

    
async def do_show_new_image_roi_dialog(new_name: str, variable_type: str, variable_tags: str, core: "PyriWebUIBrowser"):
    try:
        db = core.device_manager.get_device_subscription("variable_storage").GetDefaultClient()
        img_var_names = await db.async_filter_variables("globals","",["image"],None)

        if len(img_var_names) <= 0:
            js.alert("No source images available!")
            return

        dialog_html = importlib_resources.read_text(__package__,"new_image_roi_dialog.html")

        dialog_obj = NewImageRoiDialog(new_name, core, core.device_manager)

        el = js.document.createElement('div')
        setattr(el,"id","new_image_roi_dialog_wrapper")
        js.document.getElementById("wrapper").appendChild(el)

        dialog = js.Vue.new(to_js2({
            "el": "#new_image_roi_dialog_wrapper",
            "template": dialog_html,
            "data":
            {
                "image_selected": "",
                "image_select_options": [],
            },
            "methods":
            {
                "handle_create": dialog_obj.handle_create,
                "handle_hidden": dialog_obj.handle_hidden,
                "image_select_changed": dialog_obj.image_select_changed,
                "image_reset": dialog_obj.image_reset,
                "image_rot_m5": dialog_obj.image_rot_m5,
                "image_rot_p5": dialog_obj.image_rot_p5
            }
        }))

        dialog_obj.init_vue(dialog)

        img_vars = []
        for v in img_var_names:
            img_vars.append({"value": v, "text": v})
        getattr(dialog,"$data").image_select_options = to_js2(img_vars)
        if len(img_vars) > 0:
            getattr(dialog,"$data").image_selected = img_vars[0]["value"]
            core.create_task(dialog_obj.set_image(img_var_names[0]))
    except:
        js.alert(f"Image roi creating failed:\n\n{traceback.format_exc()}")
    
    getattr(dialog,"$bvModal").show("new_image_roi")


def show_new_image_roi_dialog(new_name: str, variable_type: str, variable_tags: str, core: "PyriWebUIBrowser"):
    core.create_task(do_show_new_image_roi_dialog(new_name, variable_type, variable_tags, core))