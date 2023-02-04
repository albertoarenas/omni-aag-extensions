from pathlib import Path

import omni.ext
import omni.ui as ui
import omni.kit
import omni.kit.menu.utils
from omni.kit.menu.utils import MenuItemDescription

from .src.menu import LookAtConstraintMenu

#VARIANTS_PNG = Path(__file__).parent.parent.parent / "data" / "variants.png"


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class AagLookAtExtension(omni.ext.IExt):
    
    def __init__(self):
        pass
    
    def on_startup(self, ext_id):
        print("[aag.lookat] aag lookat startup")
        self._extension_path = _extension_path = omni.kit.app.get_app_interface().get_extension_manager().get_extension_path(ext_id)
        self._menu = LookAtConstraintMenu()

    def create_lookat_constraint(self):
        print("create_lookat_constraint")


    def on_shutdown(self):
        print("[aag.lookat] aag lookat shutdown")
        self._menu.on_shutdown()
        self._menu = None

