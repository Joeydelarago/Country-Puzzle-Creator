from logging import Logger
from typing import List, Tuple
from pyvista import CellType, UnstructuredGrid
import json
from OSMPythonTools.nominatim import Nominatim


def create_region_puzzle(country_name: str, ouput_folder: str) -> None:
    region_ids, region_names = get_region_ids_list(country_name)
    region_bondary_points = [get_region_polygon(
        region) for region in region_ids]

    for i, polygon in enumerate(region_bondary_points):
        export_stl(polygon, region_names[i])


def get_region_polygon(region_id: str) -> List:
    nominatim = Nominatim()
    results = nominatim.query(
        f"relation/{region_id}", lookup=True, params={"polygon_geojson": 1})

    if not results:
        Logger.warning(f"No result found for region: {region_id}")
        return

    json_result = results.toJSON()[0]

    geojson = json_result["geojson"]["coordinates"]
    
    if len(geojson) > 1:
        return geojson[0][0]
    else:
        return geojson[0]
    
    poly = points_to_polygon(geojson[0][0])
    poly2 = points_to_polygon(geojson[1][0])
    
    mesh = poly.extrude((0, 0, -1.5), capping=True)
    mesh.plot(line_width=5, show_edges=True)
    
    mesh2 = poly2.extrude((0, 0, -1.5), capping=True)
    mesh2.plot(line_width=5, show_edges=True)


    return geojson[0]


def get_region_ids_list(country_name: str) -> Tuple[List[int], List[str]]:
    """
    Currently just pulling the id list using this query on https://overpass-turbo.eu/
    [out:csv(::id)][timeout:120];
    {{geocodeArea:Ireland}}->.searchArea;
    (
    relation["admin_level"="6"](area.searchArea);
    );
    out body;
    """
    return [282760, 282800, 282818, 283426, 283647, 283679, 283732, 284368, 285833, 285915, 285977, 285980, 285981, 332622, 332631, 334372, 334885, 334898, 335330, 335442, 335443, 335444, 335445, 335446, 338539, 1763195], ["County Wicklow", "County Dublin", "County Meath", "County Waterford", "County Monaghan", "County Cavan", "County Donegal", "County Leitrim", "County Kildare", "County Laois", "County Carlow", "County Kilkenny", "County Wexford", "County Kerry", "County Cork", "County Tipperary", "County Clare", "County Limerick", "County Sligo", "County Offaly", "County Roscommon", "County Galway", "County Longford", "County Westmeath", "County Mayo", "County Louth",]


def export_stl(points: List[List[int]], filename: str):
    poly = points_to_polygon(points)
    mesh = poly.extrude((0, 0, -20), capping=True)
    # mesh.plot(line_width=5, show_edges=True)
    # mesh.translate((-1000, 1000, 1000), inplace=True)
    mesh.save(f"{filename}.stl")


def points_to_polygon(points_2d: List[List[int]]):
    # Takes in points and outputs pyvista polygon. e.g.[[0, 1], [20, 0]]

    points_3d = [[point[0]*100, point[1]*100, 0] for point in points_2d]
    cells = [len(points_2d)] + list(range(len(points_2d)))
    return UnstructuredGrid(cells, [CellType.POLYGON], points_3d).extract_surface()


if __name__ == "__main__":
    create_region_puzzle("Ireland", "test")
