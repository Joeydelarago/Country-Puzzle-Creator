from trimesh import Trimesh

from mesh_generating_utils import create_mesh

def create_models(image_path: str = "test.png", output_path: str = "", invert: bool = True, flat: bool = True, max_height: int = 255, backplate: bool = False) -> None:
    pixels_mesh: Trimesh = create_mesh(image_path, invert, flat, max_height, False)
    pixels_mesh.export(output_path)

    if backplate:
        backplate_mesh: Trimesh = create_mesh(image_path, False, True, 1, True)
        backplate_mesh.export("backplate.stl")


if __name__ == "__main__":
    create_models()
