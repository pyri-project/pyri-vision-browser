import js
from RobotRaconteur.Client import *
import importlib_resources
import traceback
import numpy as np
import base64
from RobotRaconteurCompanion.Util.GeometryUtil import GeometryUtil
from pyri.webui_browser.util import to_js2

class NewImageTemplateDialog:
    def __init__(self, new_name, core, device_manager):
        self.vue = None
        self.core = core
        self.device_manager = device_manager
        self.new_name = new_name
        self.cropper = None

    def init_vue(self, vue):
        self.vue = vue

    async def do_handle_create(self, img_np, w, h):
        try:
            var_storage = self.device_manager.get_device_subscription("variable_storage").GetDefaultClient()
            compressed_img = RRN.NewStructure("com.robotraconteur.image.CompressedImage",var_storage)
            compressed_img_info = RRN.NewStructure("com.robotraconteur.image.ImageInfo",var_storage)
            compressed_img_info.width = w
            compressed_img_info.height = h
            compressed_img_info.encoding = 0x6000
            compressed_img.image_info = compressed_img_info
            compressed_img.data = img_np

            var_consts = RRN.GetConstants('tech.pyri.variable_storage', var_storage)
            variable_persistence = var_consts["VariablePersistence"]
            variable_protection_level = var_consts["VariableProtectionLevel"]

            await var_storage.async_add_variable2("globals", self.new_name ,"com.robotraconteur.image.CompressedImage", \
                RR.VarValue(compressed_img,"com.robotraconteur.image.CompressedImage"), ["image_template"], {}, \
                variable_persistence["const"], None, variable_protection_level["read_write"], \
                [], "Image matching template", False, None)

        except:
            js.alert(f"Save image template failed:\n\n{traceback.format_exc()}")
        

    def handle_create(self, *args):
        try:
            cropped_canvas = self.cropper.getCroppedCanvas(to_js2({"imageSmoothingEnabled":False}))
            img_b64 = cropped_canvas.toDataURL('image/png')
            img_b64 = img_b64.replace("data:image/png;base64,","")
            img_bytes = base64.b64decode(img_b64)
            img_np = np.frombuffer(img_bytes, np.uint8)

            self.core.create_task(self.do_handle_create(img_np, cropped_canvas.width, cropped_canvas.height))
        except:
            js.alert(f"Save image template failed:\n\n{traceback.format_exc()}")

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
                img_el = js.document.getElementById("training_image")
                img_el.src = img_src
                self.cropper = js.Cropper.new(img_el, to_js2({"viewMode":2}))
            else:
                self.cropper.reset()
                self.cropper.replace(img_src)
        except:
            traceback.print_exc()

    
async def do_show_new_image_template_dialog(new_name: str, variable_type: str, variable_tags: str, core: "PyriWebUIBrowser"):
    try:
        db = core.device_manager.get_device_subscription("variable_storage").GetDefaultClient()
        img_var_names = await db.async_filter_variables("globals","",["image"],None)

        if len(img_var_names) <= 0:
            js.alert("No source images available!")
            return

        dialog_html = importlib_resources.read_text(__package__,"new_image_template_dialog.html")

        dialog_obj = NewImageTemplateDialog(new_name, core, core.device_manager)

        el = js.document.createElement('div')
        el.id = "new_image_template_dialog_wrapper"
        js.document.getElementById("wrapper").appendChild(el)

        dialog = js.Vue.new(to_js2({
            "el": "#new_image_template_dialog_wrapper",
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
        js.alert(f"Image template creating failed:\n\n{traceback.format_exc()}")

    getattr(dialog,"$bvModal").show("new_image_template")


def show_new_image_template_dialog(new_name: str, variable_type: str, variable_tags: str, core: "PyriWebUIBrowser"):
    core.create_task(do_show_new_image_template_dialog(new_name, variable_type, variable_tags, core))