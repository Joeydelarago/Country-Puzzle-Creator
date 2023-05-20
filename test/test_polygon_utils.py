from typing import List, Tuple
import pytest

from src.map_polygon import MapPolygon
from src.polygon_utils import border_length, find_borders, simplify_polygon, simplify_polygons, normalize_polygons, export_svg


@pytest.fixture
def first_polygon() -> MapPolygon:
    return MapPolygon([(0, 0), (1, 0), (1, 1), (0, 1)])

@pytest.fixture
def second_polygon() -> MapPolygon:
    return MapPolygon([(0, 0), (1, 0), (1, -1), (0, -1)])

@pytest.fixture
def common_points(first_polygon, second_polygon) -> List[Tuple[int, int]]:
    return list(set(first_polygon.points).intersection(set(second_polygon.points)))

@pytest.fixture
def complex_polygon():
    return MapPolygon([(0, 0), (0.2, 0), (0.3, 0), (0.4, 0), (0.5, 0), (1, 0), (1, -1), (0, -1)])

def test_border_length(first_polygon):
    assert border_length(first_polygon, 0, 1) == 1
    
def test_border_length_float(complex_polygon):
    assert border_length(complex_polygon, 0, 3) == 0.4
    
def test_simplify_polygon(complex_polygon):
    assert len(simplify_polygon(complex_polygon, [(0, 5)])) == 5

def test_simplify_polygon_large(complex_polygon):
    assert len(simplify_polygon(complex_polygon, [(0, 6)])) == 4

def test_find_borders(first_polygon, common_points):
    assert len(find_borders(first_polygon, common_points)) == 1

def test_find_borders_shared(first_polygon, second_polygon, common_points):
    borders_1 = find_borders(first_polygon, common_points)
    borders_2 = find_borders(second_polygon, common_points)
    assert len(borders_1) == len(borders_2)
    assert borders_1 == borders_2
    
def test_simplify_polygons_same_size(first_polygon, second_polygon):
    polygons = simplify_polygons([first_polygon, second_polygon])
    
    assert len(polygons[0]) == len(polygons[1])
    
def test_simplify_polygons_returns_subset_of_polygon(first_polygon, second_polygon):
    polygons = simplify_polygons([first_polygon, second_polygon])
    
    assert set(polygons[0]).intersection(set(first_polygon)) == set(polygons[0])
    assert set(polygons[1]).intersection(set(second_polygon)) == set(polygons[1])

def test_normalize_polygons(first_polygon):
    polygon = normalize_polygons([first_polygon])[0]
    assert polygon.min_x() == 0
    assert polygon.min_y() == 0

def test_create_polygon_svg(first_polygon):
    export_svg([first_polygon], "test.svg")