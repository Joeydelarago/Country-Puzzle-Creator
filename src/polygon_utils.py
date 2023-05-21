import itertools
import logging
import math
import svg

from typing import List, Tuple
from simplification.cutil import simplify_coords

from map_polygon import MapPolygon

logger = logging.getLogger('polygon_utils')
logging.basicConfig()


def simplify_polygons(polygons: List[MapPolygon], snap_distance: int = 0.01) -> List[MapPolygon]:
    """ Simplify common borders between polygons

    Args:
        polygons (MapPolygon): List of polygons to simplify
        county_names (List[str]): _description_
        snap_distance (int, optional): _description_. Defaults to 400.

    Returns:
        List[List[Tuple[int, int]]]: _description_
    """
    counties_touching = 0

    # Simplify the borders between polygons
    for p1, p2 in itertools.combinations(polygons, 2):
        common_points = list(set(p1.points).intersection(set(p2.points)))  # Fast check for common border points

        if not common_points:
            # These polygons share no borders, exit early.
            continue

        borders_p1 = find_borders(p1, common_points.copy())
        borders_p2 = find_borders(p2, common_points.copy())

        borders_p1 = merge_borders(p1, borders_p1, snap_distance)
        borders_p2 = merge_borders(p2, borders_p2, snap_distance)

        if not len(borders_p1) == len(borders_p2):
            logger.warning(f"There are more borders on one county with the other. {p1.name}:{p2.name}")

        if common_points:
            counties_touching += 1

        p1.points = simplify_polygon(p1, borders_p1).points
        p2.points = simplify_polygon(p2, borders_p2).points

        p1.borders[p2] = borders_p1
        p2.borders[p1] = borders_p2

    # Simplify the borders not adjacent to polygons
    for poly in polygons:
        poly.points = simplify_polygon(poly, poly.outside_borders(), simplfy=0.1).points



    logger.info(f"counties_touching: {counties_touching}")
    
    return polygons


def find_borders(polygon: MapPolygon, common_points: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """ Finds polgons sections that contain common points 


    :param polygon: Polygon containing points
    :param common_points: list of points along border to match with polygon
    :return: List of pairs (start_index, end_index) of connected border stretches in full_border
    """
    matching_borders = []
    common = common_points.copy()
    while common:
        start_index = polygon.points.index(common[0])
        end_index = (start_index + 1) % len(polygon)
        
        while True:
            common.remove(polygon[start_index])
            
            new_start_index = start_index - 1
            if new_start_index < 0:
                new_start_index = len(polygon) - 1
                
            if polygon[new_start_index] not in common:
                break
                
            start_index = new_start_index
        
        while polygon[end_index] in common:
            common.remove(polygon[end_index])
            end_index = (end_index + 1) % (len(polygon) - 1)

        matching_borders.append((start_index, end_index))

    return matching_borders


def merge_borders(polygon: MapPolygon, borders: List[Tuple[int, int]], snap_distance: int) -> List[Tuple[int, int]]:
    """ Merge nearby borders into single border

    :param borders: List of border start->end indexes along the edge of a polygon
    :param snap_distance: Max distance between points to merge borders. This is distance between coordinates.
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
        
        # FIXME: This should get distance on a sphere
        l = math.dist(polygon[merged_border[1]], polygon[border[0]])
        if l < snap_distance:
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


def border_length(polygon: MapPolygon, start: int, end: int) -> float:
    """ Find the length of a polgon between start and end points.

    Args:
        polygon (MapPolygon): Polygon containing list of points
        start (int): The index in polygons to start counting length
        end (int): The index in polygons to stop counting length

    Returns:
        float: Distance between polgons[start] and polygons[end]
    """
    
    length = 0
    for p1, p2 in zip(polygon[start:end + 1], polygon[start + 1: end + 1]):
        length += math.dist(p1, p2)
    return length


def simplify_polygon(polygon: MapPolygon, border_indexes: List[Tuple[int, int]] = [], simplfy: float = 0.01) -> MapPolygon:
    """ Simplify sections of polygon between (start, end) index pairs from border_indexes.

    Args:
        polygon (List[Tuple[int, int]]): Polygon to be simplified
        border_indexes (List[Tuple[int, int]]): List of (start, end) indexes of border sections to be simplified
    """
    simplified_polygon = MapPolygon([], polygon.name)
    border_indexes.sort()

    if not border_indexes:
        sb = simplify_coords(polygon, simplfy)
        simplified_polygon.points.extend([(point[0], point[1]) for point in sb])
    
    for i in range(len(border_indexes)):
        start, end = border_indexes[i]
        next_start, _ = border_indexes[(i + 1) % len(border_indexes)]
        
        if start < end:
            sb = simplify_coords(polygon[start:end], simplfy)
        else:
            sb = simplify_coords(polygon[start:] + polygon[:end], simplfy)
            
        if end - 1 <= next_start: # -1 because end and start are using for slicing (slicing is end exclusive)
            b = polygon[end:next_start]
        else:
            b = polygon[end:] + polygon[:next_start]

        simplified_polygon.points.extend([(point[0], point[1]) for point in sb])
        simplified_polygon.points.extend(b)

    logger.info(f"Polygon size before: {len(polygon)} after: {len(simplified_polygon)}")

    return simplified_polygon


def export_svg(polygons: List[MapPolygon], filename: str):
    """ Export one or more polygons as SVG files """
    elements = []

    red = 0
    for poly in polygons:
        svg_poly = svg.Polygon(
            points=list(itertools.chain(*(poly.points))),
            # stroke=f"rgb({red}, 100, 100)",
            fill=f"rgb({red}, 100, 100)",
            stroke_width=5,
        ),
        red += round(255/len(polygons))
        elements.append(svg_poly)

    bounding_box = get_polygons_bounding_box(polygons)
    svg_polygons = svg.SVG(width=bounding_box[2], height=bounding_box[3], elements=elements)

    with open(filename, "w") as svg_file:
        svg_file.write(str(svg_polygons))


def get_mercator_polygon(polygon) -> MapPolygon:
    """ Transform polygon points from lat lng to mercator projection """
    mercator_points = []
    for point in polygon.points:
        lat_rad = math.radians(point[1])
        long_rad = math.radians(point[0])

        earth_radius = 6371000

        x = earth_radius * long_rad
        y = earth_radius * math.log(math.tan(math.pi / 4 + lat_rad / 2))

        mercator_points.append((x, y))

    polygon.points = mercator_points

    return polygon


def normalize_polygons(polygons: List[MapPolygon], height=1000) -> List[MapPolygon]:
    """ Normalize the coordinates of polygons between 0 and max """

    bounding_box = get_polygons_bounding_box(polygons)
    min_x = bounding_box[0]
    min_y = bounding_box[1]
    max_x = bounding_box[2]
    max_y = bounding_box[3]

    width = abs(height * ((max_x - min_x)/max_x)) # change width to match aspect ratio of bounding box

    # Adjust min to 0, 0
    for poly in polygons:
        poly.points = list(map(lambda point: (((point[0] - min_x)/(max_x - min_x))*width, ((point[1] - min_y)/(max_y - min_y))*height), poly.points))

    return polygons


def get_polygons_bounding_box(polygons: List[MapPolygon]) -> Tuple[int, int, int, int]:
    """ Returns the bounding box of a list of polygons """
    if not polygons:
        raise ValueError("Input list is empty")

    min_x = polygons[0].min_x()
    min_y = polygons[0].min_y()
    max_x = polygons[0].max_x()
    max_y = polygons[0].max_y()

    # Find min values
    for poly in polygons:
        min_x = min(poly.min_x(), min_x)
        min_y = min(poly.min_y(), min_y)
        max_x = max(poly.max_x(), max_x)
        max_y = max (poly.max_y(), max_y)

    return min_x, min_y, max_x, max_y
