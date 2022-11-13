from logging import Logger
from typing import List
from pyvista import CellType, UnstructuredGrid
import json
from OSMPythonTools.nominatim import Nominatim


def create_region_puzzle(country_name: str, ouput_folder: str) -> None:
    region_names = get_regions_list(country_name)
    region_bondary_points = [get_region_polygon(region) for region in region_names]
    
    for i, polygon in enumerate(region_bondary_points):
        export_stl(polygon, region_names[i])

def get_region_polygon(region: str) -> List:
    nominatim = Nominatim()
    results = nominatim.query(region, params={"polygon_geojson": 1})
    
    if not results:
        Logger.warning(f"No result found for region: {region}")
        return
    
    json_result = results.toJSON()[0]
    
    geojson = json_result["geojson"]["coordinates"][0]
    
    return geojson
    
    
def get_regions_list(country_name: str) -> List[str]:
    return ["Cork County Ireland"]

def export_stl(points: List[List[int]], filename: str):
    # pass
    # poly = pyvista.Polygon(n_sides=8)
    # mesh = poly.extrude((0, 0, 1.5), capping=True)
    # mesh.plot(line_width=5, show_edges=True)
    poly = points_to_polygon(points)
    
    # For debugging
    # examples.plot_cell(grid)
    # poly = pyvista.Polygon(n_sides=8)
    mesh = poly.extrude((0, 0, -1.5), capping=True)
    mesh.plot(line_width=5, show_edges=True)
    mesh.translate((-1000, 1000, 1000), inplace=True)
    mesh.save("test.stl")

def points_to_polygon(points_2d: List[List[int]]):
    # Takes in points and outputs pyvista polygon. e.g.[[0, 1], [20, 0]]

    points_3d = [[point[0]*1000, point[1]*1000, 0] for point in points_2d]
    cells = [len(points_2d)] + list(range(len(points_2d)))
    return UnstructuredGrid(cells, [CellType.POLYGON], points_3d).extract_surface()
    

if __name__ == "__main__":
    create_region_puzzle("Ireland", "test")