from pxr import Usd, UsdGeom, Sdf, Gf, Vt
import omni.usd

import omni.kit.commands

stage = omni.usd.get_context().get_stage()
print(stage)

cube_path = Sdf.Path('/World/Cube')

prim = stage.GetPrimAtPath(cube_path)
if prim:
    omni.kit.commands.execute('DeletePrims',
        paths=[str(cube_path)],
        destructive=False)


(_, cube_path) = omni.kit.commands.execute('CreateMeshPrimWithDefaultXform',
	prim_type='Cube',
	prim_path=str(cube_path),
	select_new_prim=True,
	prepend_default_prim=True)

prim = stage.GetPrimAtPath(cube_path)

def bind_material(stage, prims, mat_path):
    material_prim = stage.GetPrimAtPath(mat_path)
    material = UsdShade.Material(material_prim)
    if type(prims) is not list:
        prims = [prims]
    for prim in prims:
        binding_api = UsdShade.MaterialBindingAPI(prim)
        binding_api.Bind(material)

# imageable = UsdGeom.Imageable(prim)
# geomsubset = UsdGeom.Subset.CreateGeomSubset(
#     imageable, 
#     "Top", 
#     "face", 
#     [1],
#    'materialBind',
#    '')

# print(geomSubset)

geomSubset = UsdGeom.Subset(prim)
geomSubset.CreateElementTypeAttr("face")
geomSubset.CreateFamilyNameAttr("materialBind")

subset_name = "/World/Cube/Face1"
geomSubset = UsdGeom.Subset.Define(stage, subset_name)
geomSubset.CreateElementTypeAttr("face")
geomSubset.CreateFamilyNameAttr("materialBind")
geomSubset.CreateIndicesAttr(Vt.IntArray([1]))
bind_material(stage, geomSubset, name)






