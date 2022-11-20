import logging
from typing import List, Tuple

from OSMPythonTools.nominatim import Nominatim
from multiprocessing import Process

from polygon_utils import simplify_polygons
from stl_utils import export_stl


logger = logging.getLogger('main')
logging.basicConfig()


def create_region_puzzle(country_name: str, output_folder: str) -> None:
    county_names = get_county_names_list(country_name)
    boundary_polygons = [get_county_polygon(county) for county in county_names]
    simplified_polygons = simplify_polygons(boundary_polygons, county_names)

    for i, polygon in enumerate(simplified_polygons):
        Process(target=export_stl, args=(polygon, county_names[i], output_folder)).start()


def get_county_polygon(county: str) -> List:
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


def get_county_names_list(country_name: str) -> Tuple[List[int], List[str]]:
    return ["Wicklow", "Dublin", "Meath", "Waterford", "Monaghan", "Cavan", "Donegal", "Leitrim", "Kildare", "Laois", "Carlow", "Kilkenny", "Wexford", "Kerry", "County Cork", "Tipperary", "Clare", "Limerick", "Sligo", "Offaly", "Roscommon", "County Galway", "Longford", "Westmeath", "Mayo", "Louth", ]


if __name__ == "__main__":
    create_region_puzzle("Ireland", "test")
