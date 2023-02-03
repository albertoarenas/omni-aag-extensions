import carb
import omni.kit.actions
import omni.kit.commands
from omni.kit.menu.utils import MenuItemDescription, add_menu_items, remove_menu_items
from .commands import CreateLookAtConstraint

class LookAtConstraintMenu:
    def __init__(self):
        self.on_startup()

    def on_startup(self):
        self.menus = []
        self._settings = None

        # Register all commands
        omni.kit.commands.register(CreateLookAtConstraint)

        # register command to be used by MenuItemDescription(onclick_action)
        omni.kit.actions.core.get_action_registry().register_action(
            "aag.anim.lookatConstraint",
            "_lookat_constraint_on_clicked",
            lambda: self._lookat_constraint_on_clicked(),
            display_name="ArenasTools->Constraints->Aim Constraint",
            description="Create LookAt Constraint."
        )


        # add menu item
        self.sub_menus = [
            MenuItemDescription(
                name="LookAt Constraint",
                onclick_action=("aag.anim.lookatConstraint", "_lookat_constraint_on_clicked")
            )
        ]
        self.menus = [MenuItemDescription(name="Constraints", sub_menu=self.sub_menus)]
        add_menu_items(self.menus, "ArenasTools")

    def on_shutdown(self):
        remove_menu_items(self.menus, "ArenasTools")
        # Register all commands
        omni.kit.commands.unregister(CreateLookAtConstraint)
        self.menus = []

    def _lookat_constraint_on_clicked(self):
        # selected_paths = get_selection()
        omni.kit.commands.execute("CreateLookAtConstraint", eye=None, target=None)
        #print("_aim_constraint_on_clicked")
