import itertools
from logging import Logger
from typing import List, Tuple

from OSMPythonTools.nominatim import Nominatim
from pyvista import CellType, UnstructuredGrid
from simplification.cutil import simplify_coords


def create_region_puzzle(country_name: str, ouput_folder: str) -> None:
    region_names = get_region_ids_list(country_name)
    region_bondary_points = [get_region_polygon(region) for region in region_names]
    
    simplify_polygon_borders(region_bondary_points, region_names)

    for i, polygon in enumerate(region_bondary_points):
        export_stl(polygon, region_names[i])


def get_region_polygon(county: str) -> List:
    nominatim = Nominatim()
    results = nominatim.query("", params={"polygon_geojson": 1, "county": county, "country": "Ireland"})

    if not results:
        Logger.warning(f"No result found for county: {county}")
        return

    json_result = results.toJSON()[0]

    geojson = []
    
    if len(json_result["geojson"]["coordinates"]) > 1:
        # Choose longest list. This ignores islands and only takes the largest landmass. It does not include holes.
        geojson = max([p[0] for p in json_result["geojson"]["coordinates"]], key=len)
    else:
        geojson = json_result["geojson"]["coordinates"][0]
        
    return [(point[0], point[1]) for point in geojson]


def get_region_ids_list(country_name: str) -> Tuple[List[int], List[str]]:
    return ["Wicklow", "Dublin", "Meath", "Waterford", "Monaghan", "Cavan", "Donegal", "Leitrim", "Kildare", "Laois", "Carlow", "Kilkenny", "Wexford", "Kerry", "County Cork", "Tipperary", "Clare", "Limerick", "Sligo", "Offaly", "Roscommon", "County Galway", "Longford", "Westmeath", "Mayo", "Louth",]


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

def simplify_polygon_borders(polygons, region_names):
    # for each pair of polygons
    #    if they have overlapping border
    #        find overlapping border + simplify
    #             swap that section of border out on both polygons
        
    counties_touching = 0
    for r1, r2 in itertools.combinations(region_names, 2):
        p1 = polygons[region_names.index(r1)]
        p2 = polygons[region_names.index(r2)]
        
        common_points = set(p1).intersection(set(p2))
        
        if common_points:
            print(f"r1: {r1} r2: {r2} common_points: {len(common_points)}")
            counties_touching += 1
            
        
    print(f"region name count: {len(region_names)}")
    print(f"counties_touching: {counties_touching}")
    
    # simplified = simplify_coords(coords, 1.0)

if __name__ == "__main__":
    create_region_puzzle("Ireland", "test")
