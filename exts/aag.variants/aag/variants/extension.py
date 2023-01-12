from pathlib import Path

import omni.ext
import omni.ui as ui

from .src.create_variant import CreateVariantFromSelection

VARIANTS_PNG = Path(__file__).parent.parent.parent / "data" / "variants.png"

# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print("[aag.reviewnotes] some_public_function was called with x: ", x)
    return x**x


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class AagVariantsExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):

        print("[aag.reviewnotes] aag reviewnotes startup")

        self.create_variant_usecase = CreateVariantFromSelection()

        self._window = ui.Window("Variants", width=300, height=300)
        with self._window.frame:
            with ui.VStack():

                ui.Image(
                    str(VARIANTS_PNG),
                    height=200,
                    # fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                    alignment=ui.Alignment.CENTER,
                    style={"border_radius": 10},
                )
                ui.Spacer(height=5)

                def on_click_create_variant():
                    self.create_variant_usecase.create_variant_from_selection()

                with ui.VStack():
                    ui.Button("Create Variant", height=40, clicked_fn=lambda: on_click_create_variant())

    def on_shutdown(self):
        print("[aag.reviewnotes] aag reviewnotes shutdown")
