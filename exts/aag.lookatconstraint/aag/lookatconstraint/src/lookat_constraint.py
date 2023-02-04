import carb
import omni.usd
import omni.kit
import omni.timeline
from pxr import Gf, Sdf, Usd, UsdGeom, Vt, Tf
from enum import Enum


class AxisId(Enum):
    XPOS = 0
    YPOS = 1
    ZPOS = 2
    XNEG = 3
    YNEG = 4
    ZNEG = 5

class LookAtConstraint():

    def __init__(self):

        self._stage_event_sub = None
        self._stage_listener = None
        self._timeline_sub = None
        self._timeline = omni.timeline.get_timeline_interface()
        self._usd_context = omni.usd.get_context()
        self._xform_cache = None

        

    def __del__(self):
        self.destroy()

    def create(self):
        self.subscribe_stage_events()

        self.eye_path = None
        self.target_path = None
        selection = self.get_selection()
        if len(selection) == 2:
            self.target_path, self.eye_path = selection
        else:
            self._show_error("Please select an eye Xformable object and a target Xformable object!")
            self.destroy()
            return
        
        self.apply_constraint()

    def apply_constraint(self):
        eye = self._stage.GetPrimAtPath(self.eye_path)
        target = self._stage.GetPrimAtPath(self.target_path)
        up_vector = self._get_scene_up_vec()

        eye_matrix3x3 = self._xform_cache.GetLocalToWorldTransform(eye) 
        eye_matrix = Gf.Matrix4d(eye_matrix3x3)
        eye_pos = eye_matrix.ExtractTranslation()  
        carb.log_info(f"Eye pos: {eye_pos}") 

        target_matrix3x3 = self._xform_cache.GetLocalToWorldTransform(target) 
        target_matrix = Gf.Matrix4d(target_matrix3x3)
        target_pos = target_matrix.ExtractTranslation()
        carb.log_info(f"Target pos: {target_pos}")    

        aim_vector = (target_pos - eye_pos)
        eye_u = aim_vector.GetNormalized()
        eye_v = up_vector.GetNormalized()
        eye_w = (eye_u ^ eye_v).GetNormalized()
        eye_v = eye_w ^ eye_u

        updated_eye_mtx = Gf.Matrix4d()
        updated_eye_mtx.SetIdentity()
        updated_eye_mtx.SetRow3(0, eye_u)
        updated_eye_mtx.SetRow3(1, eye_v)
        updated_eye_mtx.SetRow3(2, eye_w)

        local_mtx = Gf.Matrix4d()
        local_mtx.SetIdentity()
        eye_aim = self._axis_to_vec(AxisId.ZNEG)
        eye_up = self._axis_to_vec(AxisId.YPOS)
        eye_ul = eye_aim.GetNormalized()
        eye_vl = eye_up.GetNormalized()
        eye_wl = (eye_ul ^ eye_vl).GetNormalized()
        eye_vl = eye_wl ^ eye_ul
        local_mtx.SetRow3(0, eye_ul)
        local_mtx.SetRow3(1, eye_vl)
        local_mtx.SetRow3(2, eye_wl)

        aim_mtx = local_mtx.GetInverse() * updated_eye_mtx


        rotation_trm = Gf.Transform(aim_mtx).GetRotation()
        print(f"Rotation Transform:{rotation_trm}")
        
        eye_translation = eye_matrix.ExtractTranslation()
        eye_matrix.SetRotateOnly(rotation_trm)
        eye_matrix.SetTranslateOnly(eye_translation)

        omni.kit.commands.execute(
            "TransformPrimCommand",
            path=self.eye_path,
            new_transform_matrix=eye_matrix,)
    

    def _get_scene_up_vec(self):
        stageUpAxis = self._stage.GetMetadata("upAxis")
        if stageUpAxis.lower() == "x":
            upVec = Gf.Vec3d([1.0, 0.0, 0.0])
        elif stageUpAxis.lower() == "z":
            upVec = Gf.Vec3d([0.0, 0.0, 1.0])
        else:
            upVec = Gf.Vec3d([0.0, 1.0, 0.0])
        return upVec
    
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

    def destroy(self):

        if self._usd_context.get_stage_state() == omni.usd.StageState.OPENED:
            self._on_stage_closing()

        self.unsubscribe_stage_events()
        self.unsubscribe_usd_obj_change()
        self.unsubscribe_timeline_event()
    
    def get_selection(self):
        return self._usd_context.get_selection().get_selected_prim_paths() or []

    def _show_error(self, msg):
        try:
            import omni.kit.notification_manager

            omni.kit.notification_manager.post_notification(msg, hide_after_timeout=False)
        except:
            carb.log_error(msg)


    def subscribe_stage_events(self):
        # subscribe to USD related events
        self._stage_event_sub = self._usd_context.get_stage_event_stream().create_subscription_to_pop(
            self._on_stage_event, name="LookAtConstraint stage event"
        )

        if self._usd_context.get_stage_state() == omni.usd.StageState.OPENED:
            self._on_stage_opened()

    def unsubscribe_stage_events(self):
        self._stage_event_sub = None


    def subscribe_usd_obj_change(self):
        self._stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._notice_changed, self._stage)

    def unsubscribe_usd_obj_change(self):
        if self._stage_listener:
            self._stage_listener.Revoke()
            self._stage_listener = None

    def subscribe_timeline_event(self):
        self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
            self._on_timeline_event
        )

    def unsubscribe_timeline_event(self):
        self._timeline_sub = None

    def _on_stage_event(self, event: carb.events.IEvent):
        if event.type == int(omni.usd.StageEventType.OPENED):
            self._on_stage_opened()
        elif event.type == int(omni.usd.StageEventType.CLOSING):
            self._on_stage_closing()

    def _on_stage_opened(self):
        carb.log_info("LookAtConstraint:Stage Open")
        
        self._stage = self._usd_context.get_stage()
        self.subscribe_usd_obj_change()

        self.subscribe_timeline_event()
        self._current_time = self._timeline.get_current_time()
        self._xform_cache = UsdGeom.XformCache(self._get_current_time_code())
        

    def _on_stage_closing(self):
        carb.log_info("LookAtConstraint:Stage Close")
        self._stage = None
        self._xform_cache = None
        self.unsubscribe_usd_obj_change()
        

    def _notice_changed(self, notice, stage):
        carb.log_info("LookAtConstraint:_notice_changed")
        for prim in notice.GetChangedInfoOnlyPaths():
             prim_path = prim.GetPrimPath() 
             if  prim_path == self.eye_path or prim_path == self.target_path:
                 self.apply_constraint()
                 return


    def _on_timeline_event(self, e: carb.events.IEvent):
        carb.log_info("LookAtConstraint:_on_timeline_event")
        if  e.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED) or e.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_CHANGED):
            current_time = e.payload["currentTime"]
            if current_time != self._current_time:
                self._current_time = current_time
                self._xform_cache.SetTime(self._get_current_time_code())
                self.apply_constraint()

    def _get_current_time_code(self):
        return Usd.TimeCode(omni.usd.get_frame_time_code(self._current_time, self._stage.GetTimeCodesPerSecond()))


