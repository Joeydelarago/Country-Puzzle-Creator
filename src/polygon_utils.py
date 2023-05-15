import itertools
import logging
import math

from typing import List, Tuple
from simplification.cutil import simplify_coords

from polygon import Polygon

logger = logging.getLogger('polygon_tils')
logging.basicConfig()


def simplify_polygons(polygons: List[Polygon], county_names: List[str], snap_distance: int = 0.01) -> List[Polygon]:
    """ Simplify common borders between polygons

    Args:
        polygons (Polygon): List of polygons to simplify
        county_names (List[str]): _description_
        snap_distance (int, optional): _description_. Defaults to 400.

    Returns:
        List[List[Tuple[int, int]]]: _description_
    """
    counties_touching = 0

    for p1, p2 in itertools.combinations(polygons, 2):
        assert isinstance(p1, Polygon)
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

        # polygons[county_names.index(county1)] = simplify_polygon(p1, borders_p1)
        # polygons[county_names.index(county2)] = simplify_polygon(p2, borders_p2)

    logger.info(f"region name count: {len(county_names)}")
    logger.info(f"counties_touching: {counties_touching}")
    
    return polygons


def find_borders(polygon: Polygon, common_points: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """ Finds polgons sections that contain common points 

    :param polygon: Polygon containing points
    :param common_points: list of points along border to match with polygon
    :return: List of pairs (start_index, end_index) of connected border stretches in full_border
    """
    matching_borders = []
    common = common_points.copy()
    while common:
        start_index = polygon.points.index(common[0])
        end_index = (start_index + 1) % (len(polygon) - 1)
        
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


def merge_borders(polygon: Polygon, borders: List[Tuple[int, int]], snap_distance: int) -> List[Tuple[int, int]]:
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


def border_length(polygon: Polygon, start: int, end: int) -> float:
    """ Find the length of a polgon between start and end points.

    Args:
        polygon (Polygon): Polygon containing list of points
        start (int): The index in polygons to start counting length
        end (int): The index in polygons to stop counting length

    Returns:
        float: Distance between polgons[start] and polygons[end]
    """
    
    length = 0
    for p1, p2 in zip(polygon[start:end + 1], polygon[start + 1: end + 1]):
        length += math.dist(p1, p2)
    return length


def simplify_polygon(polygon: Polygon, border_indexes: List[Tuple[int, int]], simplfy: int = 1.0) -> Polygon:
    """ Simplify sections of polygon between (start, end) index pairs from border_indexes.

    Args:
        polygon (List[Tuple[int, int]]): Polygon to be simplified
        border_indexes (List[Tuple[int, int]]): List of (start, end) indexes of border sections to be simplified
    """
    simplified_polygon = Polygon([], polygon.name)
    border_indexes.sort()
    
    for i in range(len(border_indexes)):
        start, end = border_indexes[i]
        next_start, _ = border_indexes[(i + 1) % len(border_indexes)]
        
        if start < end:
            sb = simplify_coords(polygon[start:end], simplfy)
        else:
            sb = simplify_coords(polygon[start:] + polygon[:end], simplfy)
            
        if end < next_start:
            b = polygon[end: next_start]
        else:
            b = polygon[end:] + polygon[:next_start]

        simplified_polygon.points.extend([(point[0], point[1]) for point in sb])
        simplified_polygon.points.extend(b)

    logger.info(f"Polygon size before: {len(polygon)} after: {len(simplified_polygon)}")

    return simplified_polygon
