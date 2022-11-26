from trimesh import Trimesh
import asyncio

from mesh_generating_utils import create_mesh


async def test_run():
    print("aosntusonthaoeuaoeuaoeu")
    await create_models()
    
async def create_models(image_path: str = "test.png", output_path: str = "", invert: bool = True, flat: bool = True, max_height: int = 255, backplate: bool = False) -> None:
    print("START")
    pixels_mesh: Trimesh = await create_mesh(image_path, invert, flat, max_height, False)
    print("END")
    pixels_mesh.export(output_path)

    if backplate:
        backplate_mesh: Trimesh = create_mesh(image_path, False, True, 1, True)
        backplate_mesh.export("backplate.stl")
    print("COMPLETED")



_loop = async_pyodide.CustomLoop()
asyncio.set_event_loop(_loop)
_loop.set_task_to_run_until_done(test_run())

