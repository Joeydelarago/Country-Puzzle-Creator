import logging
import os
from typing import List

from pyvista import CellType, UnstructuredGrid

logger = logging.getLogger('stl_utils')
logging.basicConfig()

def export_stl(points: List[List[int]], filename: str,  output_folder: str):
    logger.info(f"Starting Export: {filename}")
    poly = points_to_polygon(points)
    mesh = poly.extrude((0, 0, -20), capping=True)
    mesh.plot(line_width=5, show_edges=True)
    mesh.translate((-1000, 1000, 1000), inplace=True)
    mesh.save(os.path.join(output_folder, f"{filename}.stl"))
    logger.info(f"Finished Export: {filename}")


def points_to_polygon(points_2d: List[List[int]]):
    """ Takes in points and outputs pyvista polygon. e.g.[[0, 1], [20, 0]] """

    points_3d = [[point[0]*100, point[1]*100, 0] for point in points_2d]
    cells = [len(points_2d)] + list(range(len(points_2d)))
    return UnstructuredGrid(cells, [CellType.POLYGON], points_3d).extract_surface()