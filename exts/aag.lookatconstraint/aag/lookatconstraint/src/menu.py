import carb
import omni.kit.actions
import omni.kit.commands
from omni.kit.menu.utils import MenuItemDescription
from pxr import Tf, Usd
import omni.usd

from .commands import CreateLookAtConstraint
from .lookat_constraint import LookAtConstraint

class LookAtConstraintMenu:
    def __init__(self):
        self._lookat_constraint = None
        omni.kit.menu.utils.set_default_menu_proirity("ArenasTools", 300)
        self.on_startup()

    def on_startup(self):
        self.menus = []
        self._settings = None

        omni.kit.commands.register(CreateLookAtConstraint)

        menu_item1 = MenuItemDescription(
                name="Create LookAt Constraint",
                onclick_fn=lambda: self._create_lookat_constraint_on_clicked(),
            )
        
        menu_item2 = MenuItemDescription(
                name="Destroy LookAt Constraint",
                onclick_fn=lambda: self._destroy_lookat_constraint_on_clicked(),
            )

        self.menus = [menu_item1, menu_item2]
        omni.kit.menu.utils.add_menu_items(self.menus, "ArenasTools", 300)


    def on_shutdown(self):
        omni.kit.menu.utils.remove_menu_items(self.menus, "ArenasTools")
        omni.kit.commands.unregister(CreateLookAtConstraint)
        self.menus = []


    def _create_lookat_constraint_on_clicked(self):
        #omni.kit.commands.execute("CreateLookAtConstraint", eye=None, target=None)
        #print("_aim_constraint_on_clicked")
        self._lookat_constraint = LookAtConstraint()
        self._lookat_constraint.create()
        
    def _destroy_lookat_constraint_on_clicked(self):
        #omni.kit.commands.execute("CreateLookAtConstraint", eye=None, target=None)
        #print("_aim_constraint_on_clicked")
        if self._lookat_constraint: 
            self._lookat_constraint.destroy()
            self._lookat_constraint = None


