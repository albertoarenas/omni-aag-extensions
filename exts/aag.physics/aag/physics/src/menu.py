import logging
logger = logging.getLogger(__name__)

import carb
import omni.kit.actions
import omni.kit.commands
from omni.kit.menu.utils import MenuItemDescription
from pxr import Tf, Usd
import omni.usd

# from .commands import CreateLookAtConstraint
# from .lookat_constraint import LookAtConstraint
from .rig_car import RigCarPhysicsUtils

class PhysicsMenu:
    def __init__(self):
        self._lookat_constraint = None
        omni.kit.menu.utils.set_default_menu_proirity("ArenasTools", 300)
        self.on_startup()

    def on_startup(self):
        self.menus = []
        self._settings = None

        # omni.kit.commands.register(CreateLookAtConstraint)

        menu_item1 = MenuItemDescription(
                name="Rig Car",
                onclick_fn=lambda: self._rig_car_on_clicked(),
            )
        

        self.menus = [menu_item1]
        omni.kit.menu.utils.add_menu_items(self.menus, "ArenasTools", 300)


    def on_shutdown(self):
        omni.kit.menu.utils.remove_menu_items(self.menus, "ArenasTools")
        # omni.kit.commands.unregister(CreateLookAtConstraint)
        self.menus = []


    def _rig_car_on_clicked(self):
        #omni.kit.commands.execute("CreateLookAtConstraint", eye=None, target=None)
        logger.info("_rig_car_on_clicked")
        RigCarPhysicsUtils.create_physics_layer()
        RigCarPhysicsUtils.create_rigidbodies_colliders()
        RigCarPhysicsUtils.create_collision_group()
        RigCarPhysicsUtils.rig_wheels()
        


