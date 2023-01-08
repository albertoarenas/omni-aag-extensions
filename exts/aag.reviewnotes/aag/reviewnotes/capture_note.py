import omni.usd
import omni.kit.commands
from pxr import Usd, UsdGeom, Gf, Sdf

import omni.kit.widget

import omni.kit.usd.layers as layers
from omni.kit.widget.layers.layer_model_utils import LayerModelUtils

import carb
# LayerItem

class CaptureNote():

    def __init__(self):
        self._stage:Usd.Stage = omni.usd.get_context().get_stage()
        self.usd_context = omni.usd.get_context()
        self.layers_instance = omni.kit.widget.layers.get_instance()

    def capture_note(self):
        print("Capture Note")

        layer_model = self.layers_instance.get_layer_model()
        self.app = omni.kit.app.get_app() 

        # self._layers = layers.get_layers(self._usd_context)
        # self._layers_specs_linking = self._layers.get_specs_linking()
        # self._layers_live_syncing = self._layers.get_live_syncing()

        in_live_session = layer_model.is_in_live_session
        session_layer = layer_model.session_layer_item
        session_layer_sublayers = session_layer.sublayers

        print(session_layer_sublayers[0])
        #LayerModelUtils.save_layer_as(session_layer_sublayers[0])

        file_path = r'C:\Tmp\review.usda'
        new_layer = LayerModelUtils._create_layer(file_path)
        if not new_layer:
            carb.log_error(f"Save layer failed. Failed to create layer {file_path}")

        new_layer.TransferContent(session_layer_sublayers[0].layer)

        if not new_layer.Save():
            carb.log_error(f"Save layer failed. Failed to save layer {file_path}")


        # omni.kit.commands.execute('RemovePrimSpec',
        #     layer_identifier='omniverse://586893a3-c6df-4743-bf39-08a38b37a332.cne.ngc.nvidia.com/Projects/Testees/review_notes/.live/review_session_test_scene.live/Review.live/root.live',
        #     prim_spec_path=[Sdf.Path('/World')])
