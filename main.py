import itertools
import logging
from typing import List, Tuple

from OSMPythonTools.nominatim import Nominatim
from pyvista import CellType, UnstructuredGrid
from simplification.cutil import simplify_coords

logger = logging.getLogger('main')


def create_region_puzzle(country_name: str, ouput_folder: str) -> None:
    region_names = get_region_ids_list(country_name)
    region_bondary_points = [get_region_polygon(region) for region in region_names]

    simplify_polygon_borders(region_bondary_points, region_names)

    for i, polygon in enumerate(region_bondary_points):
        # export_stl(polygon, region_names[i])
        pass


def get_region_polygon(county: str) -> List:
    nominatim = Nominatim()
    results = nominatim.query("", params={"polygon_geojson": 1, "county": county, "country": "Ireland"})

    if not results:
        logger.warning(f"No result found for county: {county}")
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
    return ["Wicklow", "Dublin", "Meath", "Waterford", "Monaghan", "Cavan", "Donegal", "Leitrim", "Kildare", "Laois", "Carlow", "Kilkenny", "Wexford", "Kerry", "County Cork", "Tipperary", "Clare", "Limerick", "Sligo", "Offaly", "Roscommon", "County Galway", "Longford", "Westmeath", "Mayo", "Louth", ]


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


def simplify_polygon_borders(polygons: List[List[Tuple[int, int]]], region_names: List[str], snap_distance: int = 400) -> None:
    # for each pair of polygons
    #    if they have overlapping border
    #        find overlapping border + simplify
    #             swap that section of border out on both polygons

    counties_touching = 0
    for r1, r2 in itertools.combinations(region_names, 2):
        p1 = polygons[region_names.index(r1)]
        p2 = polygons[region_names.index(r2)]

        common_points = list(set(p1).intersection(set(p2)))

        if not common_points:
            continue

        borders_p1 = find_borders(p1, common_points.copy())
        borders_p2 = find_borders(p2, common_points.copy())

        borders_p1 = merge_borders(borders_p1, snap_distance)
        borders_p2 = merge_borders(borders_p2, snap_distance)


        if not len(borders_p1) == len(borders_p2):
            logger.warning(f"There are more borders on one county with the other. {r1}:{r2}")
            print(f"b1: {borders_p1} b2: {borders_p2}")

            # print(f"bp1: {borders_p1} bp2: {borders_p2}")

        if common_points:
            # print(f"r1: {r1} r2: {r2} common_points: {len(common_points)}")
            counties_touching += 1

    print(f"region name count: {len(region_names)}")
    print(f"counties_touching: {counties_touching}")

    # simplified = simplify_coords(coords, 1.0)


def find_borders(full_border: List[Tuple[int, int]], points: List[int]):
    """ Finds borders that contain common points 
    :param full_border: List of pairs of points on a closed polygon
    :param points: 
    :return: List of pairs (start_index, end_index) of connected border stretches in full_border
    """
    matching_borders = []

    while points:
        start_index = full_border.index(points[0])
        end_index = (start_index + 1) % (len(full_border) - 1)
        
        while True:
            points.remove(full_border[start_index])
            
            new_start_index = start_index - 1
            if new_start_index < 0:
                new_start_index = len(full_border) - 1
                
            if full_border[new_start_index] not in points:
                break
                
            start_index = new_start_index
        
        while full_border[end_index] in points:
            points.remove(full_border[end_index])
            end_index = (end_index + 1) % (len(full_border) - 1)

        matching_borders.append((start_index, end_index))

    return matching_borders


def merge_borders(borders: List[Tuple[int, int]], snap_distance: int) -> List[Tuple[int, int]]:
    """ Merge nearby borders into single border
    
    :param borders: List of borders along the edge of a polygon
    :param snap_distance: Max distance between points to merge borders. This is distance in list not in km.
    """
    if len(borders) <= 1:
        return borders
    borders.sort()

    merged_borders = []

    merged_border = None
    for border in borders:
        if not merged_border:
            merged_border = border
            continue

        if abs(merged_border[1] - border[0]) < snap_distance:
            merged_border = (merged_border[0], border[1])
        else:
            merged_borders.append(merged_border)
            merged_border = None 
            
    if len(merged_borders) == 1:
        return merged_borders
    
    if merged_border:
        merged_borders.append(merged_border)
    
    # Merge first and last elements
    first = merged_borders[0]
    last = merged_borders[len(merged_borders) - 1]
    if abs(first[0] - last[1]) < snap_distance:
        merged_border = merged_border = (last[1], first[0])
        merged_borders = merged_borders[1:-1]
        merged_borders.append(merged_border)
    
    return merged_borders


if __name__ == "__main__":
    create_region_puzzle("Ireland", "test")
