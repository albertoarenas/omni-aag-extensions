import re
import pathlib

import logging
logger = logging.getLogger(__name__)

from pxr import Usd, UsdGeom, Sdf, UsdPhysics

import omni.kit.commands
import omni.usd



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
    def find_prim_by_name(stage:Usd.Stage, prim_name):
        for prim in stage.TraverseAll():
            if prim.GetName() == prim_name:
                return prim
        return None
    
    @staticmethod
    def find_xform_by_name(stage:Usd.Stage, prim_name):
        for prim in stage.TraverseAll():
            if prim.GetName() == prim_name and prim.IsA(UsdGeom.Xform) and prim.IsActive():
                return prim
        return None

    @staticmethod
    def find_xforms(stage:Usd.Stage):
        xforms = []
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Xform) and prim.IsActive():
                xforms.append(prim)
        return xforms
    
    @staticmethod
    def create_rigidbodies_colliders(geo_prim_name="Geo"):

        stage:Usd.Stage = omni.usd.get_context().get_stage()
        geo_prim:Usd.Prim = RigCarPhysicsUtils.find_xform_by_name(stage, geo_prim_name)
        
        physics_actors_prims = None
        if geo_prim and geo_prim.IsValid():
            geo_prim_path_str = str(geo_prim.GetPath())
            all_xforms = RigCarPhysicsUtils.find_xforms(stage)
            physics_actors_prims = [xform for xform in all_xforms 
                                    if (geo_prim_path_str in str(xform.GetPath())) and xform != geo_prim]

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

        mass_info = [{'id':'', 'mass':1, 'apply_parent':False},
                     {'id':'', 'mass':1, 'apply_parent':False},
                     {'id':'', 'mass':1, 'apply_parent':False},
                     {'id':'', 'mass':1, 'apply_parent':False},
                     {'id':'', 'mass':1, 'apply_parent':False},
                     {'id':'', 'mass':1, 'apply_parent':False},]







    @staticmethod
    def rig_wheels(chassis_prim_name="chassis", wheels_prim_name="wheels_B"):
        logger.info("rig_wheels()")

        stage:Usd.Stage = omni.usd.get_context().get_stage()
        new_joint_name = f"RJ_{chassis_prim_name}_{wheels_prim_name}"
        existing_joint = RigCarPhysicsUtils.find_prim_by_name(stage, new_joint_name)
        if not existing_joint:

            chassis_prim:Usd.Prim = RigCarPhysicsUtils.find_xform_by_name(stage, chassis_prim_name)
            wheels_prim:Usd.Prim = RigCarPhysicsUtils.find_xform_by_name(stage, wheels_prim_name)

            (_, new_joint) = omni.kit.commands.execute('CreateJointCommand',
                                # stage=Usd.Stage.Open(rootLayer=Sdf.Find(root_layer), sessionLayer=Sdf.Find('anon:000002114D16DD80'), pathResolverContext=None),
                                # stage=Usd.Stage.Open(rootLayer=Sdf.Find('omniverse://586893a3-c6df-4743-bf39-08a38b37a332.cne.ngc.nvidia.com/Projects/LiveEdit/Friday_Live/DirectorLive/RepositoryStaging/assets/prop/lego/lego_car_v1/lego_car_v1_asset.usd'), sessionLayer=Sdf.Find('anon:000002114D16DD80'), pathResolverContext=None),
                                stage=stage,
                                joint_type='Revolute',
                                from_prim=chassis_prim,
                                to_prim=wheels_prim)
            
            new_joint.GetAttribute("physics:axis").Set('Z')

            wheels_prim_path:Sdf.Path = wheels_prim.GetPath()
            new_joint_path = wheels_prim_path.AppendPath(new_joint_name)
            omni.kit.commands.execute('MovePrims',
                paths_to_move={new_joint.GetPath(): new_joint_path},
                destructive=False)


        



