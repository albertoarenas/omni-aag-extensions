from pathlib import Path

import omni.ext
import omni.ui as ui
import omni.kit
import omni.kit.menu.utils
from omni.kit.menu.utils import MenuItemDescription

from .src.menu import PhysicsMenu

#VARIANTS_PNG = Path(__file__).parent.parent.parent / "data" / "variants.png"



class AagPhysicsExtension(omni.ext.IExt):
    
    def __init__(self):
        pass
    
    def on_startup(self, ext_id):
        print("[aag.physics] aag physics startup")
        self._extension_path = _extension_path = omni.kit.app.get_app_interface().get_extension_manager().get_extension_path(ext_id)
        self._menu = PhysicsMenu()



    def on_shutdown(self):
        print("[aag.physics] aag physics shutdown")
        self._menu.on_shutdown()
        self._menu = None

