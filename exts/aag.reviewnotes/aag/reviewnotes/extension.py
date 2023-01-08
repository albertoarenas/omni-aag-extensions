import omni.ext
import omni.ui as ui

from .capture_note import CaptureNote

# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print("[aag.reviewnotes] some_public_function was called with x: ", x)
    return x ** x


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class AagReviewnotesExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):

        print("[aag.reviewnotes] aag reviewnotes startup")
        self.capture_note_usecase = CaptureNote()

        self._window = ui.Window("Review Notes", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                label = ui.Label("")


                def on_click():
                    self.capture_note_usecase.capture_note()

                with ui.HStack():
                    ui.Button("Capture Notes", clicked_fn=on_click)

    def on_shutdown(self):
        print("[aag.reviewnotes] aag reviewnotes shutdown")
