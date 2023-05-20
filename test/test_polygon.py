from typing import List, Tuple
import pytest

from src.map_polygon import MapPolygon
from src.polygon_utils import border_length, find_borders, simplify_polygon, simplify_polygons


@pytest.fixture
def polygon() -> MapPolygon:
    return MapPolygon([(0, 0), (1, 0), (1, -1), (0, -1)])

@pytest.fixture
def polygon2() -> MapPolygon:
    return MapPolygon([(0, 0), (1, 0), (1, 1), (0, 1)])

@pytest.fixture
def borders() -> List[Tuple[int, int]]:
    return [(0, 0), (1, 0)]

@pytest.fixture
def complex_polygon():
    return [(0, 0), (0.2, 0), (0.3, 0), (0.4, 0), (0.5, 0), (1, 0), (1, -1), (0, -1)]

def test_min_x(polygon):
    assert polygon.min_x() == 0

def test_min_y(polygon):
    assert polygon.min_y() == -1

def test_max_x(polygon):
    assert polygon.max_x() == 1

def test_max_y(polygon):
    assert polygon.max_y() == 0

def test_add_borders(polygon, polygon2, borders):
    polygon.extend_borders(borders, polygon2)
    assert polygon.borders[polygon2] == borders