import logging
logger = logging.getLogger(__name__)

from pxr import Usd, Sdf

usd_scene_path = "omniverse://586893a3-c6df-4743-bf39-08a38b37a332.cne.ngc.nvidia.com/Projects/LiveEdit/Friday_Live/DirectorLive/RepositoryStaging/assets/prop/chess_board/caballo/caballo_blanco.usd"

stage:Usd.Stage = Usd.Stage.Open(usd_scene_path)
logger.info(stage)

default_prim:Usd.Prim = stage.GetDefaultPrim()
logger.info(default_prim.GetName())

# all_payloads = []
# for prim_spec in default_prim.GetPrimStack():
#     if prim_spec.hasPayloads:
#         all_payloads.extend(prim_spec.payloadList.GetAddedOrExplicitItems())
# payload_path = all_payloads[0].assetPath
# logger.info(payload_path)

if default_prim.HasPayload():
    default_prim_spec = stage.GetEditTarget().GetLayer().GetPrimAtPath(default_prim.GetPath())
    payload_path = default_prim_spec.payloadList.GetAddedOrExplicitItems()[0].assetPath
    logger.info(payload_path)


    default_prim_payloads:Usd.Payloads = default_prim.GetPayloads()

    old_payload=Sdf.Payload(payload_path)
    default_prim_payloads.RemovePayload(old_payload)
    new_payload_path = f"{payload_path[:2]}geo/{payload_path[2:]}"
    logger.info(new_payload_path)
    new_payload=Sdf.Payload(new_payload_path)
    default_prim_payloads.AddPayload(new_payload)

# import omni.kit.commands
# from pxr import Usd, Sdf

# omni.kit.commands.execute('ReplacePayload',
# 	stage=Usd.Stage.Open(rootLayer=Sdf.Find('omniverse://586893a3-c6df-4743-bf39-08a38b37a332.cne.ngc.nvidia.com/Projects/LiveEdit/Friday_Live/DirectorLive/RepositoryStaging/assets/prop/chess_board/caballo/caballo_blanco.usd'), sessionLayer=Sdf.Find('anon:000001D8893B2640'), pathResolverContext=None),
# 	prim_path=Sdf.Path('/world'),
# 	old_payload=Sdf.Payload('./caballo.usdc'),
# 	new_payload=Sdf.Payload('./geo/caballo.usdc'))
