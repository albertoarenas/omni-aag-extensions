import re
import pathlib

import logging
logger = logging.getLogger(__name__)

from pxr import Usd, UsdGeom

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
    def rig_wheels():
        logger.info("rig_wheels()")
