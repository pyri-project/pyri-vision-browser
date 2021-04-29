from typing import List, Dict, Callable, Any, Tuple
from pyri.webui_browser.plugins.variable_dialog import PyriWebUIBrowserVariableDialogInfo, PyriWebUIBrowserVariableDialogPluginFactory, PyriWebUIBrowserVariableDialogBase
from pyri.webui_browser import PyriWebUIBrowser
from .new_calibrate_intrinsic_dialog import show_new_camera_calibration_intrinsic_dialog
from .new_calibrate_extrinsic_dialog import show_new_camera_calibration_extrinsic_dialog
from .new_calibrate_robot_origin_dialog import show_new_robot_origin_calibration_dialog
from .new_image_template_dialog import show_new_image_template_dialog
from .new_image_roi_dialog import show_new_image_roi_dialog

_variable_dialog_infos = {
    ("com.robotraconteur.imaging.camerainfo.CameraCalibration",("camera_calibration_intrinsic")): \
        PyriWebUIBrowserVariableDialogInfo(
            "vision_camera_calibration_intrinsic",
            "Camera Calibration Intrinsic",
            "com.robotraconteur.imaging.camerainfo.CameraCalibration",
            ["camera_calibration_intrinsic"],
            "Camera Intrinsic Calibration Parameters",
        ),
    ("com.robotraconteur.geometry.NamedPoseWithCovariance",("camera_calibration_extrinsic")): \
        PyriWebUIBrowserVariableDialogInfo(
            "vision_camera_calibration_extrinsic",
            "Camera Calibration Extrinsic",
            "com.robotraconteur.geometry.NamedPoseWithCovariance",
            ["camera_calibration_extrinsic"],
            "Camera Extrinsic Calibration Parameters"
        ),

    ("com.robotraconteur.geometry.NamedPoseWithCovariance",("robot_origin_pose_calibration")): \
        PyriWebUIBrowserVariableDialogInfo(
            "robot_origin_pose_calibration",
            "Robot Origin Pose Calibration",
            "com.robotraconteur.geometry.NamedPoseWithCovariance",
            ["robot_origin_pose_calibration"],
            "Robot Origin Pose Calibration"
        ),
    ("com.robotraconteur.image.CompressedImage",("image_template")): \
        PyriWebUIBrowserVariableDialogInfo(
            "image_template",
            "Image Template",
            "com.robotraconteur.image.CompressedImage",
            ["image_template"],
            "Template image for matching"
        ),
    ("com.robotraconteur.geometry.BoundingBox2D",("image_roi")): \
        PyriWebUIBrowserVariableDialogInfo(
            "image_roi",
            "Image ROI",
            "com.robotraconteur.geometry.BoundingBox2D",
            ["image_roi"],
            "Image Region of Interest (ROI)"
        )
}

class PyriVisionWebUIBrowserVariableDialogPluginFactory(PyriWebUIBrowserVariableDialogPluginFactory):
    def __init__(self):
        super().__init__()

    def get_plugin_name(self) -> str:
        return "pyri-vision-browser"

    def get_variable_dialog_infos(self) -> Dict[Tuple[str,Tuple[str]],PyriWebUIBrowserVariableDialogInfo]:
        return _variable_dialog_infos

    def show_variable_new_dialog(self, new_name: str, variable_type: str, variable_tags: str, core: "PyriWebUIBrowser") -> None:
        if variable_type == "com.robotraconteur.imaging.camerainfo.CameraCalibration" and "camera_calibration_intrinsic" in variable_tags:
            show_new_camera_calibration_intrinsic_dialog(new_name, variable_type, variable_tags, core)
            return
        if variable_type == "com.robotraconteur.geometry.NamedPoseWithCovariance" and "camera_calibration_extrinsic" in variable_tags:
            show_new_camera_calibration_extrinsic_dialog(new_name, variable_type, variable_tags, core)
            return
        if variable_type == "com.robotraconteur.geometry.NamedPoseWithCovariance" and "robot_origin_pose_calibration" in variable_tags:
            show_new_robot_origin_calibration_dialog(new_name, variable_type, variable_tags, core)
            return
        if variable_type == "com.robotraconteur.image.CompressedImage" and "image_template" in variable_tags:
            show_new_image_template_dialog(new_name, variable_type, variable_tags, core)
            return
        if variable_type == "com.robotraconteur.geometry.BoundingBox2D" and "image_roi" in variable_tags:
            show_new_image_roi_dialog(new_name, variable_type, variable_tags, core)
            return
        assert False, "Invalid new variable dialog type requested"

    def show_variable_edit_dialog(self, variable_name: str, variable_type: str, variable_tags: List[str], core: "PyriWebUIBrowser") -> None:
        raise NotImplementedError()

def get_webui_browser_variable_dialog_factory():
    return PyriVisionWebUIBrowserVariableDialogPluginFactory()
    