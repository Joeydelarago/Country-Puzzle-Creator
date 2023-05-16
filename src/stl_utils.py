import logging
import os
from typing import List, Tuple

from pyvista import CellType, UnstructuredGrid

logger = logging.getLogger('stl_utils')
logging.basicConfig()

def export_stl(points: List[Tuple[int, int]], filename: str,  output_folder: str) -> None:
    logger.info(f"Starting Export: {filename}")
    poly = points_to_pyvista_polygon(points)
    mesh = poly.extrude((0, 0, -2), capping=True)
    mesh.save(os.path.join(output_folder, f"{filename}.stl"))
    logger.info(f"Finished Export: {filename}")
    
def show_merged_stl(polygons: List[List[Tuple[int, int]]]) -> None:
    """ Show extruded polygons on plot. Each polygon is plotted with an increased z coordinate.

    Args:
        polygons (List[List[Tuple[int, int]]]): List of polygons, each polygon is a list edges (x, y tuples)
    """
    mesh = None
    
    for i, polygon in enumerate(polygons):
        pyvista_polygon = points_to_pyvista_polygon(polygon)
        
        if mesh:
            mesh = mesh.merge(pyvista_polygon.extrude((0, 0, -20), capping=True).translate((0, 0, 10*i)))
        else:
            mesh = pyvista_polygon.extrude((0, 0, -20), capping=True)
            
    mesh.plot(show_edges=True, line_width=5)


def points_to_pyvista_polygon(points_2d: List[Tuple[int, int]]) -> UnstructuredGrid:
    """ Takes in List of polygon edges as (x, y) Tuples and outputs pyvista polygon. """
    points_3d = [[point[0]*20, point[1]*20, 0] for point in points_2d]
    cells = [len(points_2d)] + list(range(len(points_2d)))
    return UnstructuredGrid(cells, [CellType.POLYGON], points_3d).extract_surface()