from pathlib import Path

import omni.ext
import omni.ui as ui

from .src.create_variant import CreateVariantFromSelection
from .src.create_props import CreatePropsFrom3DSmax

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

        #print("[aag.reviewnotes] aag reviewnotes startup")

        self.create_variant_usecase = CreateVariantFromSelection()
        self.create_props_usecase = CreatePropsFrom3DSmax()

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

                def on_click_create_props():
                    PROP_EXPORT_PATH = "omniverse://586893a3-c6df-4743-bf39-08a38b37a332.cne.ngc.nvidia.com/Projects/LiveEdit/Friday_Live/DirectorLive/RepositoryStaging/3DSMax/buildings"
                    PROP_PATH = "omniverse://586893a3-c6df-4743-bf39-08a38b37a332.cne.ngc.nvidia.com/Projects/LiveEdit/Friday_Live/DirectorLive/RepositoryStaging/assets/prop/buildings"
                    MATERIAL_OVER_PATH = "omniverse://586893a3-c6df-4743-bf39-08a38b37a332.cne.ngc.nvidia.com/Projects/LiveEdit/Friday_Live/DirectorLive/RepositoryStaging/assets/prop/buildings/bldg_looks_render/bldg_looks_render.usd"
                    ASSET_VARIANT_NAME = "bldg_variant.usd"
                    self.create_props_usecase.create_props(PROP_EXPORT_PATH, PROP_PATH, MATERIAL_OVER_PATH, ASSET_VARIANT_NAME)

                with ui.VStack():
                    ui.Button("Create Variant", height=40, clicked_fn=lambda: on_click_create_variant())
                    ui.Button("Create Props", height=40, clicked_fn=lambda: on_click_create_props())

    def on_shutdown(self):
        #print("[aag.reviewnotes] aag reviewnotes shutdown")
        pass
