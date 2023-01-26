from typing import List

import logging
logger = logging.getLogger(__name__)

import omni.client
import os

from pxr import Usd, UsdGeom, Gf, Sdf

class NucleusFS():

    @staticmethod
    def exist(url:str) -> bool:
        result, entry = omni.client.stat(url)
        return result == omni.client.Result.OK

    @staticmethod
    def folder_exists(url:str) -> bool:
        result, entry = omni.client.stat(url)
        return (result == omni.client.Result.OK) & NucleusFS.is_folder_from_entry(entry)

    @staticmethod
    def file_exists(url:str) -> bool:
        result, entry = omni.client.stat(url)
        return (result == omni.client.Result.OK) & NucleusFS.is_file_from_entry(entry)

    @staticmethod
    def is_folder_from_entry(entry:omni.client.ListEntry) -> bool:
        return (entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN)

    @staticmethod
    def is_file_from_entry(entry:omni.client.ListEntry) -> bool:
        return (entry.flags & omni.client.ItemFlags.READABLE_FILE)


    @staticmethod
    def list_folders(url:str) -> List[str]:
      
        return NucleusFS.list_content_by_criteria(url, NucleusFS.is_folder_from_entry)

    @staticmethod
    def list_files(url:str) -> List[str]:
        return NucleusFS.list_content_by_criteria(url, NucleusFS.is_file_from_entry)

    @staticmethod
    def list_content_by_criteria(url:str, criteria) -> List[str]:
        content_urls = []
        _, entries = omni.client.list(url)
        for entry in entries:
            if criteria(entry):
                content_url = entry.relative_path
                content_urls.append(content_url)
                # logger.info(content_url)
        
        return content_urls



    @staticmethod
    def create_folder(url:str) -> bool:
        result = omni.client.create_folder(url)
        return (result == omni.client.Result.OK)

	
class CreatePropsException(Exception):
    pass

class CreatePropsFrom3DSmax():

    def __init__(self):
        logger.info("CreatePropsFrom3DSmax created")

    def create_props(self, props_export_url:str, assets_prop_url:str, material_over_url:str, asset_variant_name:str):

        # Get export folder
        props_folder_names = NucleusFS.list_folders(props_export_url)
        
        asset_prop_variant_urls = []

        # Go through all export folders
        for prop_folder_name in props_folder_names:
            
            # Get exported USD files
            exported_prop_folder_url = f"{props_export_url}/{prop_folder_name}"
            exported_prop_files = NucleusFS.list_files(exported_prop_folder_url)

            if len(exported_prop_files) != 2:
                error_msg = f"Only two exported files expected per prop. Found {len(exported_prop_files)} files: {exported_prop_files}"
                logger.error(error_msg)
                raise CreatePropsException(error_msg)

            # Create asset folders if needed
            asset_prop_folder_url =f"{assets_prop_url}/{prop_folder_name}"
            asset_prop_render_folder_url = f"{asset_prop_folder_url}/render"
            asset_prop_proxy_folder_url = f"{asset_prop_folder_url}/proxy"
            
            if not NucleusFS.folder_exists(asset_prop_folder_url):
                NucleusFS.create_folder(asset_prop_folder_url)
                NucleusFS.create_folder(asset_prop_render_folder_url)
                NucleusFS.create_folder(asset_prop_proxy_folder_url)

            # Get proxy file
            proxy_exported_prop_file =   exported_prop_files[0] if "proxy" in exported_prop_files[0] else exported_prop_files[1]
            logger.info(f"Proxy: {proxy_exported_prop_file}")

            # Create proxy mesh usd
            proxy_exported_prop_url = f"{exported_prop_folder_url}/{proxy_exported_prop_file}"
            proxy_asset_prop_url = f"{asset_prop_proxy_folder_url}/{proxy_exported_prop_file}"
            if not NucleusFS.file_exists(proxy_asset_prop_url):
                self.create_proxy_mesh_usd(proxy_exported_prop_url, proxy_asset_prop_url)
            
            # Create render mesh usd
            render_exported_prop_file =   exported_prop_files[1] if "proxy" in exported_prop_files[0] else exported_prop_files[0]
            logger.info(f"Render: {render_exported_prop_file}")
            render_exported_prop_url = f"{exported_prop_folder_url}/{render_exported_prop_file}"
            render_asset_prop_url = f"{asset_prop_render_folder_url}/{render_exported_prop_file}"
            if not NucleusFS.file_exists(render_exported_prop_url):
                self.create_render_mesh_usd(render_exported_prop_url, render_asset_prop_url, material_over_url)

            # Create variants
            asset_prop_variant_url = f"{asset_prop_folder_url}/{prop_folder_name}_variant.usd"
            asset_prop_variant_urls.append(asset_prop_variant_url)
            self.create_prop_variant(proxy_asset_prop_url, render_asset_prop_url, asset_prop_variant_url)

        asset_variant_usd_url = f"{assets_prop_url}/{asset_variant_name}"
        self.create_asset_variant(asset_variant_usd_url, asset_prop_variant_urls)

    def create_asset_variant(self, asset_variant_usd_url:str, asset_variant_urls:List[str]):

        try:
            stage = Usd.Stage.CreateNew(asset_variant_usd_url)
        except:
            stage = Usd.Stage.Open(asset_variant_usd_url)

        logger.info(f"Opened: {asset_variant_usd_url}")
        
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
        world_xform_prim = UsdGeom.Xform.Define(stage, "/World")
        world_prim: Usd.Prim = stage.GetPrimAtPath("/World")
        stage.SetDefaultPrim(world_prim)
        
        vset = world_prim.GetVariantSets().AddVariantSet('assetSet')
        for asset_variant_url in asset_variant_urls:
            variant_set_name = os.path.splitext(os.path.basename(asset_variant_url))[0]
            vset.AddVariant(variant_set_name)
            vset.SetVariantSelection(variant_set_name)
            with vset.GetVariantEditContext():
                world_prim.GetPayloads().AddPayload(asset_variant_url)



        stage.Save()
        stage = None

        logger.info(f"Saved: {asset_variant_usd_url}")
            
    def create_proxy_mesh_usd(self, exported_usd_url:str, asset_usd_url:str):

        try:
            stage = Usd.Stage.CreateNew(asset_usd_url)
        except:
            stage = Usd.Stage.Open(asset_usd_url)

        logger.info(f"Opened: {asset_usd_url}")
        
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
        world_xform_prim = UsdGeom.Xform.Define(stage, "/World")
        world_prim: Usd.Prim = stage.GetPrimAtPath("/World")
        world_prim.GetPayloads().AddPayload(exported_usd_url)
        stage.SetDefaultPrim(world_prim)
        stage.Save()
        stage = None

        logger.info(f"Saved: {asset_usd_url}")


    def create_render_mesh_usd(self, exported_usd_url:str, asset_usd_url:str, material_usd_url:str):

        try:
            stage = Usd.Stage.CreateNew(asset_usd_url)
        except:
            stage = Usd.Stage.Open(asset_usd_url)

        logger.info(f"Opened: {asset_usd_url}")
        
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
        world_xform_prim = UsdGeom.Xform.Define(stage, "/World")
        world_prim: Usd.Prim = stage.GetPrimAtPath("/World")
        world_prim.GetPayloads().AddPayload(exported_usd_url)
        stage.SetDefaultPrim(world_prim)
        
        try:
            root_layer: Sdf.Layer = stage.GetRootLayer()
            sub_layer: Sdf.Layer = Sdf.Layer.FindOrOpen(material_usd_url)
            # You can use standard python list.insert to add the subLayer to any position in the list
            if sub_layer not in root_layer.subLayerPaths:
                root_layer.subLayerPaths.append(sub_layer.identifier)
        except:
            logger.warning(f"Layer exists: {material_usd_url}")

        stage.Save()
        stage = None

        logger.info(f"Saved: {asset_usd_url}")


    def create_prop_variant(self, asset_proxy_usd_url:str, asset_render_usd_url:str, asset_usd_url:str):

        try:
            stage = Usd.Stage.CreateNew(asset_usd_url)
        except:
            stage = Usd.Stage.Open(asset_usd_url)

        logger.info(f"Opened: {asset_usd_url}")
        
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
        world_xform_prim = UsdGeom.Xform.Define(stage, "/World")
        world_prim: Usd.Prim = stage.GetPrimAtPath("/World")
        stage.SetDefaultPrim(world_prim)
        
        vset = world_prim.GetVariantSets().AddVariantSet('modelSet')
        vset.AddVariant('proxy')
        vset.SetVariantSelection('proxy')
        with vset.GetVariantEditContext():
            world_prim.GetPayloads().AddPayload(asset_proxy_usd_url)

        vset.AddVariant('render')
        vset.SetVariantSelection('render')
        with vset.GetVariantEditContext():
            world_prim.GetPayloads().AddPayload(asset_render_usd_url)

        stage.Save()
        stage = None

        logger.info(f"Saved: {asset_usd_url}")
            


    


    @staticmethod
    def is_folder(entry):
        return (entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN) > 0


