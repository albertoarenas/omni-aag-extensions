

# For python it is recommended to use std python logging, which also redirected to Carbonite
# It also captures file path and loc
import logging
logger = logging.getLogger(__name__)
logger.info("123")
logger.warning("456")
logger.error("789")

import omni.client

SERVER_URL = "omniverse://586893a3-c6df-4743-bf39-08a38b37a332.cne.ngc.nvidia.com"
PATH = "omniverse://586893a3-c6df-4743-bf39-08a38b37a332.cne.ngc.nvidia.com/Projects/LiveEdit/Friday_Live/DirectorLive/RepositoryStaging/assets/prop/buildings/bldg_sm_trailer/surfacing"

result = omni.client.create_folder(PATH)
if result == omni.client.Result.OK:
	print("Great")
	
import asyncio
import omni.kit.app
import omni.client


async def my_task():
    logger = logging.getLogger(__name__)
    logger.info(f"my task begin")

	# Wait few updates:
    for i in range(5):
        e = await omni.kit.app.get_app().next_update_async()
        logger.info(f"{i}: {e}")

	# Native asyncio.sleep
    await asyncio.sleep(2)

	# Async List using Client Library
    LIST_PATH = SERVER_URL
    (result, entries) = await omni.client.list_async(LIST_PATH)
    for e in entries:
        logger.info(e)

    logger.info(f"my task end")

# Start task
asyncio.ensure_future(my_task())

# stage = Usd.Stage.CreateNew(temp_usd_file_path)
# await omni.kit.app.get_app().next_update_async()
# UsdGeom.Xform.Define(stage, '/xform')
# UsdGeom.Sphere.Define(stage, '/xform/sphere')
# await omni.kit.app.get_app().next_update_async()
# stage.Save()