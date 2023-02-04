import carb
import omni.usd
import omni.kit.commands

from pxr import Gf, Sdf, Usd, UsdGeom, Vt
from enum import Enum

import numpy as np

class AxisId(Enum):
    XPOS = 0
    YPOS = 1
    ZPOS = 2
    XNEG = 3
    YNEG = 4
    ZNEG = 5

class CreateLookAtConstraint(omni.kit.commands.Command):
    
    def __init__(
        self,
        eye=None,
        target=None,
        up_vector=[0.0, 1.0, 0.0],
    ):
        
        if eye is None and target is None:
            selection = self.get_selection()
            if len(selection) == 2:
                target, eye = selection
            else:
                carb.log_error("Please select an eye Xformable object and a target Xformable object!")
                return
        elif eye and target:
            pass
        else:
            carb.log_error("Invalid inputs! Please provide both eye and target Xformable objects!")
            return

        self.eye_path = eye
        self.target_path = target

        # self._usd_undo = None


    
    def get_selection(self):
        """
        get a selected object list from scene
        """
        return omni.usd.get_context().get_selection().get_selected_prim_paths() or []

    def do(self):
        stage = omni.usd.get_context().get_stage()
        self.eye = stage.GetPrimAtPath(self.eye_path)
        self.target = stage.GetPrimAtPath(self.target_path)
        self.up_vector = self._get_scene_up_vec()

        # usd_undo = UsdLayerUndo(stage.GetEditTarget().GetLayer())
        # usd_undo.reserve(self.eye.GetPath().AppendChild("aimConstraint_grp").pathString)

        
        eye_matrix3x3 = UsdGeom.XformCache().GetLocalToWorldTransform(self.eye) 
        eye_matrix = Gf.Matrix4d(eye_matrix3x3)
        eye_pos = eye_matrix.ExtractTranslation()  
        carb.log_info(f"Eye pos: {eye_pos}") 

        target_matrix3x3 = UsdGeom.XformCache().GetLocalToWorldTransform(self.target) 
        target_matrix = Gf.Matrix4d(target_matrix3x3)
        target_pos = target_matrix.ExtractTranslation()
        carb.log_info(f"Target pos: {target_pos}")    

        aim_vector = (target_pos - eye_pos)
        eyeU = aim_vector.GetNormalized()
        eyeV = self.up_vector.GetNormalized()
        eyeW = (eyeU ^ eyeV).GetNormalized()
        eyeV = eyeW ^ eyeU

        updatedEyeMtx = Gf.Matrix4d()
        updatedEyeMtx.SetIdentity()
        updatedEyeMtx.SetRow3(0, eyeU)
        updatedEyeMtx.SetRow3(1, eyeV)
        updatedEyeMtx.SetRow3(2, eyeW)

        localMtx = Gf.Matrix4d()
        localMtx.SetIdentity()
        eye_aim = self._axis_to_vec(AxisId.ZNEG)
        eye_up = self._axis_to_vec(AxisId.YPOS)
        eyeUL = eye_aim.GetNormalized()
        eyeVL = eye_up.GetNormalized()
        eyeWL = (eyeUL ^ eyeVL).GetNormalized()
        eyeVL = eyeWL ^ eyeUL
        localMtx.SetRow3(0, eyeUL)
        localMtx.SetRow3(1, eyeVL)
        localMtx.SetRow3(2, eyeWL)

        aimMtx = localMtx.GetInverse() * updatedEyeMtx


        mat = Gf.Matrix4d()
        mat.SetTranslateOnly(Gf.Vec3d(10.0, 1.0, 1.0))
        mat.SetRotateOnly(Gf.Rotation(Gf.Vec3d(0, 1, 0), 290))  

        # if state:
        #    self._usd_undo = usd_undo
        #    carb.log_info("Aim constraint created")

        rotation_trm = Gf.Transform(aimMtx).GetRotation()
        print(f"Rotation Transform:{rotation_trm}")
        
        # rotation_euler = rotation_trm.Decompose(Gf.Vec3d.XAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.ZAxis())
        # rotation_vec2 = Gf.Vec3d(rotation_euler)
        # print(f"Rotation Vec2:{rotation_vec2}")

        # self.eye = stage.GetPrimAtPath(self.eye_path)
        # hasXformOp = self.eye.HasAttribute('xformOp:rotateXYZ')
        # rotateYXZ = self.eye.GetAttribute('xformOp:rotateXYZ')
        # rotateYXZ.Set(rotation_vec)

        # quaternion: Gf.Quaternion = rotation_trm.GetQuaternion()

        # w = quaternion.GetReal()
        # x, y, z = [*Gf.Vec3d(quaternion.GetImaginary())]

        # # Convert Quat to Euler Vectorized
        # y_sqr = y * y

        # t0 = 2.0 * (w * x + y * z)
        # t1 = 1.0 - 2.0 * (x * x + y_sqr)
        # roll = np.arctan2(t0, t1)

        # t2 = 2.0 * (w * y - z * x)
        # pitch = -1 * np.arcsin(t2)

        # t3 = 2.0 * (w * z + x * y)
        # t4 = 1.0 - 2.0 * (y_sqr + z * z)
        # yaw = np.arctan2(t3, t4)

        # rotation_vec3 = Gf.Vec3d(Gf.RadiansToDegrees(roll), Gf.RadiansToDegrees(pitch), Gf.RadiansToDegrees(yaw))
        # print(f"Rotation Vec3:{rotation_vec3}")
        
        
        # property_path = f"{self.eye_path}.xformOp:rotateYXZ"
        # self._change_property(property_path, rotation_vec2)
        eye_translation = eye_matrix.ExtractTranslation()
        eye_matrix.SetRotateOnly(rotation_trm)
        eye_matrix.SetTranslateOnly(eye_translation)
        omni.kit.commands.execute(
            "TransformPrimCommand",
            path=self.eye_path,
            new_transform_matrix=eye_matrix,)
        

        # eye_xform = UsdGeom.Xformable(self.eye)
        # transform = eye_xform.AddTransformOp()
        # mat = Gf.Matrix4d()
        # mat.SetIdentity()
        # mat.SetRotateOnly(rotation)
        # transform.Set(mat)


    def _change_property(self, property_path, value):
        import omni.kit.commands
        from pxr import Gf, Sdf

        omni.kit.commands.execute('ChangeProperty',
            prop_path=Sdf.Path(property_path),
            value=value,
            prev=Gf.Vec3d(0.0, 0.0, 0.0))


    def _axis_to_vec(self, axis: AxisId):
        if axis == AxisId.XPOS:
            return Gf.Vec3d([1.0, 0.0, 0.0])
        elif axis == AxisId.YPOS:
            return Gf.Vec3d([0.0, 1.0, 0.0])
        elif axis == AxisId.ZPOS:
            return Gf.Vec3d([0.0, 0.0, 1.0])
        elif axis == AxisId.XNEG:
            return Gf.Vec3d([-1.0, 0.0, 0.0])
        elif axis == AxisId.YNEG:
            return Gf.Vec3d([0.0, -1.0, 0.0])
        elif axis == AxisId.ZNEG:
            return Gf.Vec3d([0.0, 0.0, -1.0])
        else:
            return

    def _get_scene_up_vec(self):
        stage = omni.usd.get_context().get_stage()
        stageUpAxis = stage.GetMetadata("upAxis")
        if stageUpAxis.lower() == "x":
            upVec = Gf.Vec3d([1.0, 0.0, 0.0])
        elif stageUpAxis.lower() == "z":
            upVec = Gf.Vec3d([0.0, 0.0, 1.0])
        else:
            upVec = Gf.Vec3d([0.0, 1.0, 0.0])
        return upVec

    def undo(self):
        return
        # if self._usd_undo is None:
        #    return
        # self._usd_undo.undo()
