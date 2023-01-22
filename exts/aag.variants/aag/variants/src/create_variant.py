import enum

from pxr import Usd, UsdGeom, Gf, Sdf
import omni.usd
import omni.kit.notification_manager as nm
import carb


class VariantType(enum.Enum):
    REFERENCE = 0
    PAYLOAD = 1


class CreateVariantFromSelection:
    def __init__(self):
        pass

    def create_variant_from_selection(
        self,
        variant_set_name: str = "GeomVis",
        variant_prim_name: str = "VariantPrim",
        type: VariantType = VariantType.PAYLOAD,
    ):
        context = omni.usd.get_context()
        stage: Usd.Stage = omni.usd.get_context().get_stage()

        # Get selected prims
        selected_prims = [stage.GetPrimAtPath(m) for m in context.get_selection().get_selected_prim_paths()]
        if not selected_prims or len(selected_prims) < 2:
            carb.log_error("ERROR: Nothing or only one primitive was selected.")
            return False

        # Create variant prim
        default_prim_path = stage.GetDefaultPrim().GetPath()
        variant_prim_path = default_prim_path.AppendPath(variant_prim_name)
        variant_xform_prim = UsdGeom.Xform.Define(stage, variant_prim_path)
        variant_prim: Usd.Prim = stage.GetPrimAtPath(variant_prim_path)

        # Create variant sets
        variant_set = variant_prim.GetVariantSets().AddVariantSet(variant_set_name)
        for prim in selected_prims:
            variant_name = prim.GetName()
            all_payloads = []
            for prim_spec in prim.GetPrimStack():
                if prim_spec.hasPayloads:
                    all_payloads.extend(prim_spec.payloadList.GetAddedOrExplicitItems())
            payload_path = all_payloads[0].assetPath

            variant_set.AddVariant(variant_name)
            variant_set.SetVariantSelection(variant_name)
            with variant_set.GetVariantEditContext():
                if type == VariantType.REFERENCE:
                    variant_prim.GetReferences().AddReference(Sdf.Reference(payload_path))
                if type == VariantType.PAYLOAD:
                    variant_prim.GetPayloads().AddPayload(Sdf.Payload(payload_path))

    def create_variant2(self):

        self._stage = omni.usd.get_context().get_stage()

        # Get selected prim
        selected_prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
        print(selected_prim_paths)
        if not selected_prim_paths or len(selected_prim_paths) > 1:
            carb.log_error("ERROR: Nothing was selected or multiple selection.")
            return

        selected_prim_path = selected_prim_paths[0]
        print(selected_prim_path)
        selected_prim = self._stage.GetPrimAtPath(Sdf.Path(selected_prim_path))
        selected_prim_name = selected_prim.GetName()

        # Get selected prim children list
        selected_prim_children = selected_prim.GetChildren()
        print(selected_prim_children)

        # Get payload paths
        payload_paths = []
        variant_names = []
        child_paths = []
        for child_prim in selected_prim_children:
            payloads: Usd.Payloads = child_prim.GetPayloads()
            print(child_prim)
            ref_and_layers = omni.usd.get_composed_payloads_from_prim(child_prim)
            # print(ref_and_layers)
            # print(ref_and_layers[0][0].assetPath)
            payload_paths.append(ref_and_layers[0][0].assetPath)
            variant_names.append(child_prim.GetName())

            child_paths.append(child_prim.GetPath())

        # Delete children
        omni.kit.commands.execute("DeletePrims", paths=child_paths, destructive=False)

        # Add a variant set
        variantset_name = selected_prim_name
        varset = selected_prim.GetVariantSets().AddVariantSet(variantset_name)

        for i, payload_path in enumerate(payload_paths):
            variant_name = variant_names[i]
            varset.AddVariant(variant_name)
            varset.SetVariantSelection(variant_name)
            with varset.GetVariantEditContext():
                selected_prim.GetPayloads().AddPayload(Sdf.Payload(payload_path))

        varset.SetVariantSelection(variant_names[0])
