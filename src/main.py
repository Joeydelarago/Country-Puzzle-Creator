import logging
from typing import List, Tuple

from OSMPythonTools.nominatim import Nominatim
from multiprocessing import Process

from polygon_utils import simplify_polygons, export_svg, normalize_polygons, get_mercator_polygon
from map_polygon import MapPolygon
from stl_utils import export_stl, show_merged_stl


logger = logging.getLogger('main')
logging.basicConfig()


def create_region_puzzle(country_name: str, output_folder: str) -> None:
    county_names = get_county_names_list(country_name)
    county_polygons = [get_county_polygon(county) for county in county_names]
    county_polygons = simplify_polygons(county_polygons)
    county_polygons = [get_mercator_polygon(poly) for poly in county_polygons]

    export_svg(normalize_polygons(county_polygons), "test.svg")  # Debug

    for i, polygon in enumerate(county_polygons):
        Process(target=export_stl, args=(polygon, polygon.name, output_folder)).start()


def get_county_polygon(county: str) -> MapPolygon:
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

    return MapPolygon([(point[0], point[1]) for point in geojson], county)


def get_county_names_list(country_name: str) -> Tuple[List[int], List[str]]:
    return ["Wicklow", "Dublin", "Meath", "Waterford", "Monaghan", "Cavan", "Donegal", "Leitrim", "Kildare", "Laois", "Carlow", "Kilkenny", "Wexford", "Kerry", "County Cork", "Tipperary", "Clare", "Limerick", "Sligo", "Offaly", "Roscommon", "County Galway", "Longford", "Westmeath", "Mayo", "Louth", ]


if __name__ == "__main__":
    create_region_puzzle("Ireland", "output")