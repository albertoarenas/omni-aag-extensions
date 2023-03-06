import re
import pathlib
import json
from typing import List, Optional, Union

import logging
logger = logging.getLogger(__name__)

from pxr import Usd, UsdGeom, Sdf, Gf, UsdPhysics

import omni.kit.commands
import omni.usd
import omni.client

class RigCarRecipe():
    
    def __init__(self):
        self.url = None
        self.json_data = None

    def load(self, url:str):
        self.url = url
        (result, version, content) = omni.client.read_file(self.url)
        if result == omni.client.Result.OK:
            self.json_data = json.loads(memoryview(content).tobytes())

    def __str__(self):
        if self.json_data:
            return json.dumps(self.json_data, indent=4)
        else:
            return ""


class RigCarPhysicsUtils():

    # Define the regular expression pattern to match a URL
    url_pattern = r'^(?:omniverse)://(?P<domain>[^/]+)(?P<path>/.*)?$'

    def __init__(self):
        pass

    
    @staticmethod
    def create_physics_layer():   
        stage:Usd.Stage = omni.usd.get_context().get_stage()
        
        # Get the root layer
        root_layer = stage.GetRootLayer()
        root_layer_url = root_layer.identifier
        logger.info(f"Root layer path: {root_layer_url}")

        physics_layer_url = None
        physics_layer_name = None
        omni_protocol = "omniverse://"
        if omni_protocol in root_layer_url:
            result = re.match(RigCarPhysicsUtils.url_pattern, root_layer_url)
            url_domain = result.group('domain')
            url_path = result.group('path')
            logger.info(f"Root layer path domain: {url_domain}")
            logger.info(f"Root layer path path: {url_path}")

            url_path = pathlib.PurePosixPath(url_path)
            logger.info(f"filename: {url_path.stem}")
            logger.info(f"extension: {url_path.suffix}")

            stem = url_path.stem
            fields = stem.split('_')
            fields[-1] = 'physics'
            new_stem = '_'.join(fields)
            new_name = f"{new_stem}.usd"
            new_path = url_path.with_name(new_name)
            physics_layer_url = omni_protocol + url_domain + str(new_path)
            physics_layer_name = new_name
            logger.info(f"Physics layer url: {physics_layer_url}")
            
        else:
            raise Exception("Root is not in omniverse")

        physics_layer = None
        for sublayer in stage.GetLayerStack():
            sublayer_url = str(sublayer.identifier) 
            if  sublayer_url == physics_layer_url:
                physics_layer = sublayer
                logger.info(f"Sublayer: {sublayer.identifier}")
                break

        if not physics_layer:
            omni.kit.commands.execute('CreateSublayer',
                layer_identifier=root_layer_url,
                sublayer_position=0,
                new_layer_path=physics_layer_url,
                transfer_root_content=False,
                create_or_insert=True,
                layer_name=physics_layer_name)


        omni.kit.commands.execute('SetEditTarget',
            layer_identifier=physics_layer_url)


    @staticmethod
    def find_prim_by_name(stage:Usd.Stage, prim_name) -> Optional[Usd.Prim]:
        for prim in stage.TraverseAll():
            if prim.GetName() == prim_name:
                return prim
        return None
    
    @staticmethod
    def find_all_prim_contains_pattern(stage:Usd.Stage, pattern) -> List[Usd.Prim]:
        all_prims = []
        for prim in stage.Traverse(Usd.TraverseInstanceProxies(Usd.PrimIsActive and Usd.PrimIsDefined and Usd.PrimIsLoaded)):
            if pattern in prim.GetName():
                all_prims.append(prim)
        return all_prims

    @staticmethod
    def find_xform_by_name(stage:Usd.Stage, prim_name:str) -> Optional[Usd.Prim]: 
        for prim in stage.TraverseAll():
            if prim.GetName() == prim_name and prim.IsA(UsdGeom.Xform) and prim.IsActive():
                return prim
        return None

    @staticmethod
    def find_xforms(stage:Usd.Stage):
        xforms = []
        # stage.Traverse(Usd.TraverseInstanceProxies(Usd.PrimIsActive and Usd.PrimIsDefined and Usd.PrimIsLoaded))
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Xform) and prim.IsActive():
                xforms.append(prim)
        return xforms
    
    @staticmethod
    def create_rigidbodies_colliders(geo_prim_name="Geo"):

        def is_parent_xform(prim):

            children = prim.GetFilteredChildren(Usd.PrimIsDefined & ~Usd.PrimIsAbstract & Usd.PrimIsActive)
            for child in children:
                if child.IsA(UsdGeom.Xform):
                    return True
                
            return False

        stage:Usd.Stage = omni.usd.get_context().get_stage()
        geo_prim:Usd.Prim = RigCarPhysicsUtils.find_xform_by_name(stage, geo_prim_name)
        
        physics_actors_prims = None
        if geo_prim and geo_prim.IsValid():
            geo_prim_path_str = str(geo_prim.GetPath())
            all_xforms = RigCarPhysicsUtils.find_xforms(stage)
            physics_actors_prims = [xform for xform in all_xforms 
                                    if (geo_prim_path_str in str(xform.GetPath())) and 
                                        (xform != geo_prim) and
                                        not is_parent_xform(xform)]

        logger.info(physics_actors_prims)

        for actor in physics_actors_prims:

            if not actor.HasAttribute("physics:rigidBodyEnabled"):
                omni.kit.commands.execute('SetRigidBody',
                    path=actor.GetPath(),
                    approximationShape='convexHull',
                    kinematic=False)
                
    @staticmethod
    def create_collision_group(collision_group_path = '/World/CollisionGroup', geo_path = '/World/Geo'):

        stage:Usd.Stage = omni.usd.get_context().get_stage()

        collision_group_prim = stage.GetPrimAtPath(collision_group_path)
        if not collision_group_prim:

            omni.kit.commands.execute('AddCollisionGroupCommand',
                stage=stage,
                path=collision_group_path)
            
            collision_group_prim = stage.GetPrimAtPath(collision_group_path)

            omni.kit.commands.execute('AddRelationshipTarget',
                relationship=collision_group_prim.GetRelationship('collection:colliders:includes'),
                target=Sdf.Path(geo_path))
            

            omni.kit.commands.execute('AddRelationshipTarget',
                relationship=collision_group_prim.GetRelationship('physics:filteredGroups'),
                target=collision_group_prim.GetPath())
            


    @staticmethod
    def create_masses():

        all_mass_info = [{'id':'11955', 'mass':0.2, 'apply_parent':False},
                         {'id':'47157', 'mass':0.43, 'apply_parent':False},
                         {'id':'23948', 'mass':1.65, 'apply_parent':False},
                         {'id':'3034', 'mass':2.27, 'apply_parent':False},
                         {'id':'32530', 'mass':0.64, 'apply_parent':False},
                         {'id':'3648', 'mass':1.17, 'apply_parent':False},
                         {'id':'3703', 'mass':5.87, 'apply_parent':False},
                         {'id':'44309', 'mass':11.15, 'apply_parent':False},
                         {'id':'4519', 'mass':0.43, 'apply_parent':False},
                         {'id':'54087', 'mass':4.33, 'apply_parent':False},
                         {'id':'59143', 'mass':33.5, 'apply_parent':True},
                         {'id':'87513', 'mass':83.94, 'apply_parent':True},]
        
        for mass_info in all_mass_info:

            stage:Usd.Stage = omni.usd.get_context().get_stage()

            # Find the prim
            all_prims = RigCarPhysicsUtils.find_all_prim_contains_pattern(stage, mass_info['id'])

            for cur_prim in all_prims:
                
                # Check if apply_parent and select parent
                prim_add_mass:Usd.Prim = cur_prim
                if mass_info['apply_parent']:
                    parent_path = cur_prim.GetPath().GetParentPath()
                    prim_add_mass = stage.GetPrimAtPath(parent_path)

                RigCarPhysicsUtils.create_and_update_mass(prim_add_mass, mass_info['mass'])
    
                
    @staticmethod
    def create_and_update_mass(prim, mass):
        # Check if mass is already present if not
        if not prim.HasAttribute('physics:mass'):

            # Add mass
            omni.kit.commands.execute('AddPhysicsComponent',
                usd_prim=prim,
                component='PhysicsMassAPI')
    
        prim.GetAttribute('physics:mass').Set(mass)



    @staticmethod
    def rig_car_joins():

        # Create Revolute Joints
        all_revolute_joins_info = [{'from':'chassis', 'to':'wheels_B'},
                                   {'from':'chassis', 'to':'wheels_F'},
                                   {'from':'motor_body', 'to':'gear_drive'}]
        
        for revolute_join_info in all_revolute_joins_info:
            RigCarPhysicsUtils.create_revolute_joins(revolute_join_info['from'], revolute_join_info['to'])

        # Create Fixed Joints
        all_fixed_joins_info = [{'from':'chassis', 'to':'motor_body'},
                                {'from':'chassis', 'to':'battery'}]
        
        for fixed_join_info in all_fixed_joins_info:
            RigCarPhysicsUtils.create_fixed_join(fixed_join_info['from'], fixed_join_info['to'])

        # Create Gear Joints
        all_gear_joins_info = [{'from':'gear_drive', 'to':'wheels_F', 'gear_ratio':-0.33}]
        for gear_join_info in all_gear_joins_info:
            RigCarPhysicsUtils.create_gear_join(gear_join_info['from'], gear_join_info['to'], gear_join_info['gear_ratio'])

        #  Replace Wheel Colliders with Cylinders
        stage:Usd.Stage = omni.usd.get_context().get_stage()
        wheel_mesh_id = '44309'
        all_wheel_meshes = RigCarPhysicsUtils.find_all_prim_contains_pattern(stage, wheel_mesh_id)
        all_wheel_meshes = [wheel_mesh for wheel_mesh in all_wheel_meshes if 'collider' not in wheel_mesh.GetName()]
        for wheel_mesh in all_wheel_meshes:
            RigCarPhysicsUtils.replace_wheels_colliders(wheel_mesh)


        # Add Forces
        all_forces_info =[{'prim_name':'wheels_F'},
                          {'prim_name': 'gear_drive'}]
        for force_info in all_forces_info:
            RigCarPhysicsUtils.add_force(force_info['prim_name'])

        # Add Physics Materials to the Ground an Wheels
        RigCarPhysicsUtils.add_physics_materials()


    @staticmethod
    def add_physics_materials():
        
        stage:Usd.Stage = omni.usd.get_context().get_stage()

        default_prim_path = stage.GetDefaultPrim().GetPath()
        ground_mat_path = default_prim_path.AppendPath('ground_physics_material')

        if not stage.GetPrimAtPath(ground_mat_path):
            omni.kit.commands.execute('AddRigidBodyMaterialCommand',
                                    stage=stage,
                                    path=str(ground_mat_path))
            
            ground_collision_plane = RigCarPhysicsUtils.find_prim_by_name(stage, 'CollisionPlane')
        
            omni.kit.commands.execute('BindMaterialExt',
                                    material_path=str(ground_mat_path),
                                    prim_path=[str(ground_collision_plane.GetPath())],
                                    strength=['weakerThanDescendants'],
                                    material_purpose='physics')
        
        wheels_mat_path = default_prim_path.AppendPath('wheels_physics_material')
        if not stage.GetPrimAtPath(wheels_mat_path):
            omni.kit.commands.execute('AddRigidBodyMaterialCommand',
                                    stage=stage,
                                    path=str(wheels_mat_path))
        
            all_wheels_prims = RigCarPhysicsUtils.find_all_prim_contains_pattern(stage, '44309')
            all_wheels_prims = [prim for prim in all_wheels_prims if 'collider' in prim.GetName()]

            for wheel_prim in all_wheels_prims:
                omni.kit.commands.execute('BindMaterialExt',
                                        material_path=str(wheels_mat_path),
                                        prim_path=[str(wheel_prim.GetPath())],
                                        strength=['weakerThanDescendants'],
                                        material_purpose='physics')




    @staticmethod
    def add_force(prim_name:str):

        stage:Usd.Stage = omni.usd.get_context().get_stage()
        prim = RigCarPhysicsUtils.find_prim_by_name(stage, prim_name)

        if not prim.HasAttribute('physxForce:force'):

            omni.kit.commands.execute('AddPhysicsComponent',
                usd_prim=prim,
                component='ForceAPI')




    @staticmethod
    def replace_wheels_colliders(wheel_prim:Usd.Prim):

        # Check if the wheel has already a collider that needs to be replaced
        if not wheel_prim.HasAttribute('physics:collisionEnabled'):
            return

        stage:Usd.Stage = omni.usd.get_context().get_stage()

        translation = Gf.Vec3d()
        if wheel_prim.HasAttribute('xformOp:translate'):
            translation = wheel_prim.GetAttribute('xformOp:translate').Get()
            logger.info(f"Wheel translation: {translation}")
        
        # Create collider name and path
        wheel_prim_parent_path:Sdf.Path = wheel_prim.GetPath().GetParentPath()
        new_collider_name = f"{wheel_prim.GetName()}_collider"
        new_collider_path = wheel_prim_parent_path.AppendPath(new_collider_name)

        # Create collider shape prim
        wheel_radius = 2.23
        wheel_height = 2.16
        omni.kit.commands.execute('CreatePrimWithDefaultXform',
            prim_type='Cylinder',
            prim_path=str(new_collider_path),
            attributes={'radius': wheel_radius, 'height': wheel_height},
            select_new_prim=True)
        
        # Apply translation to the collider
        new_collider_prim:Usd.Prim = stage.GetPrimAtPath(new_collider_path)
        new_collider_prim.GetAttribute('xformOp:translate').Set(translation)
        

        # Add Physics collider
        omni.kit.commands.execute('AddPhysicsComponent',
                                   usd_prim=new_collider_prim,
                                   component='PhysicsCollisionAPI')
        
        # Get mass info
        mass = wheel_prim.GetAttribute('physics:mass').Get()
        RigCarPhysicsUtils.create_and_update_mass(new_collider_prim, mass)

        # Remove Collision from the wheel
        omni.kit.commands.execute('RemovePhysicsComponent',
            usd_prim=wheel_prim,
            component='PhysicsCollisionAPI',
            multiple_api_token=None)

        # Hide New Collider
        omni.kit.commands.execute('ToggleVisibilitySelectedPrims',
        selected_paths=[str(new_collider_path)])




    @staticmethod
    def get_child_revolute_join(prim):
            children = prim.GetFilteredChildren(Usd.PrimIsDefined & ~Usd.PrimIsAbstract & Usd.PrimIsActive)
            for child in children:
                if child.GetTypeName() == "PhysicsRevoluteJoint":
                    return child

            return None    
            

    @staticmethod
    def create_gear_join(from_prim_name, to_prim_name, gear_ratio):

        stage:Usd.Stage = omni.usd.get_context().get_stage()
        new_joint_name = f"GJ_{from_prim_name}_{to_prim_name}"
        existing_joint = RigCarPhysicsUtils.find_prim_by_name(stage, new_joint_name)
        if not existing_joint:

            from_prim:Usd.Prim = RigCarPhysicsUtils.find_xform_by_name(stage, from_prim_name)
            to_prim:Usd.Prim = RigCarPhysicsUtils.find_xform_by_name(stage, to_prim_name)

            (_, new_joint) = omni.kit.commands.execute('CreateJointCommand',
                                                        stage=stage,
                                                        joint_type='Gear',
                                                        from_prim=from_prim,
                                                        to_prim=to_prim)
            
            # find from_prim revolute join
            from_prim_revolute_join = RigCarPhysicsUtils.get_child_revolute_join(from_prim)
            logger.info(from_prim_revolute_join)

            omni.kit.commands.execute('AddRelationshipTarget',
                relationship=new_joint.GetRelationship('physics:hinge0'),
                target=from_prim_revolute_join.GetPath())

            
            to_prim_revolute_join = RigCarPhysicsUtils.get_child_revolute_join(to_prim)
            logger.info(to_prim_revolute_join)
            omni.kit.commands.execute('AddRelationshipTarget',
                relationship=new_joint.GetRelationship('physics:hinge1'),
                target=to_prim_revolute_join.GetPath())

            new_joint.GetAttribute('physics:gearRatio').Set(gear_ratio)
            
            # omni.kit.commands.execute('ChangeProperty',
            #     prop_path=Sdf.Path('/World/Geo/wheels_F/GearJoint.physics:gearRatio'),
            #     value=-3.0,
            #     prev=1.0,
            #     target_layer=Sdf.Find('omniverse://586893a3-c6df-4743-bf39-08a38b37a332.cne.ngc.nvidia.com/Projects/LiveEdit/Friday_Live/DirectorLive/RepositoryStaging/assets/prop/lego/lego_car_v1/lego_car_v1_physics.usd'),
            #     usd_context_name=Usd.Stage.Open(rootLayer=Sdf.Find('omniverse://586893a3-c6df-4743-bf39-08a38b37a332.cne.ngc.nvidia.com/Projects/LiveEdit/Friday_Live/DirectorLive/RepositoryStaging/assets/prop/lego/lego_car_v1/lego_car_v1_asset.usd'), sessionLayer=Sdf.Find('anon:000002116A879E50'), pathResolverContext=None))



            to_prim_path:Sdf.Path = to_prim.GetPath()
            new_joint_path = to_prim_path.AppendPath(new_joint_name)
            omni.kit.commands.execute('MovePrims',
                                      paths_to_move={new_joint.GetPath(): new_joint_path},
                                      destructive=False)











    @staticmethod
    def create_fixed_join(from_prim_name, to_prim_name):

        stage:Usd.Stage = omni.usd.get_context().get_stage()
        new_joint_name = f"GJ_{from_prim_name}_{to_prim_name}"
        existing_joint = RigCarPhysicsUtils.find_prim_by_name(stage, new_joint_name)
        if not existing_joint:

            from_prim:Usd.Prim = RigCarPhysicsUtils.find_xform_by_name(stage, from_prim_name)
            to_prim:Usd.Prim = RigCarPhysicsUtils.find_xform_by_name(stage, to_prim_name)

            (_, new_joint) = omni.kit.commands.execute('CreateJointCommand',
                                                        stage=stage,
                                                        joint_type='Fixed',
                                                        from_prim=from_prim,
                                                        to_prim=to_prim)
            

            
            to_prim_path:Sdf.Path = to_prim.GetPath()
            new_joint_path = to_prim_path.AppendPath(new_joint_name)
            omni.kit.commands.execute('MovePrims',
                                      paths_to_move={new_joint.GetPath(): new_joint_path},
                                      destructive=False)


    @staticmethod
    def create_revolute_joins(from_prim_name="chassis", to_prim_name="wheels_B", axis_name='Z'):
        logger.info("rig_wheels()")

        stage:Usd.Stage = omni.usd.get_context().get_stage()
        new_joint_name = f"RJ_{from_prim_name}_{to_prim_name}"
        existing_joint = RigCarPhysicsUtils.find_prim_by_name(stage, new_joint_name)
        if not existing_joint:

            from_prim:Usd.Prim = RigCarPhysicsUtils.find_xform_by_name(stage, from_prim_name)
            to_prim:Usd.Prim = RigCarPhysicsUtils.find_xform_by_name(stage, to_prim_name)

            (_, new_joint) = omni.kit.commands.execute('CreateJointCommand',
                                                        # stage=Usd.Stage.Open(rootLayer=Sdf.Find(root_layer), sessionLayer=Sdf.Find('anon:000002114D16DD80'), pathResolverContext=None),
                                                        # stage=Usd.Stage.Open(rootLayer=Sdf.Find('omniverse://586893a3-c6df-4743-bf39-08a38b37a332.cne.ngc.nvidia.com/Projects/LiveEdit/Friday_Live/DirectorLive/RepositoryStaging/assets/prop/lego/lego_car_v1/lego_car_v1_asset.usd'), sessionLayer=Sdf.Find('anon:000002114D16DD80'), pathResolverContext=None),
                                                        stage=stage,
                                                        joint_type='Revolute',
                                                        from_prim=from_prim,
                                                        to_prim=to_prim)
            
            new_joint.GetAttribute("physics:axis").Set(axis_name)

            wheels_prim_path:Sdf.Path = to_prim.GetPath()
            new_joint_path = wheels_prim_path.AppendPath(new_joint_name)
            omni.kit.commands.execute('MovePrims',
                paths_to_move={new_joint.GetPath(): new_joint_path},
                destructive=False)


        



