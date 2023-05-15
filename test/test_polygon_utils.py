from typing import List, Tuple
import pytest

from polygon import Polygon
from polygon_utils import border_length, find_borders, simplify_polygon, simplify_polygons, normalize_polygons


@pytest.fixture
def first_polygon() -> Polygon:
    return Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])

@pytest.fixture
def second_polygon() -> Polygon:
    return Polygon([(0, 0), (1, 0), (1, -1), (0, -1)])

@pytest.fixture
def common_points(first_polygon, second_polygon) -> List[Tuple[int, int]]:
    return list(set(first_polygon.points).intersection(set(second_polygon.points)))

@pytest.fixture
def complex_polygon():
    return Polygon([(0, 0), (0.2, 0), (0.3, 0), (0.4, 0), (0.5, 0), (1, 0), (1, -1), (0, -1)])

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
    polygons = simplify_polygons([first_polygon, second_polygon], ["first_poly", "second_poly"])
    
    assert len(polygons[0]) == len(polygons[1])
    
def test_simplify_polygons_returns_subset_of_polygon(first_polygon, second_polygon):
    polygons = simplify_polygons([first_polygon, second_polygon], ["first_poly", "second_poly"])
    
    assert set(polygons[0]).intersection(set(first_polygon)) == set(polygons[0])
    assert set(polygons[1]).intersection(set(second_polygon)) == set(polygons[1])