import logging
import pickle
from typing import List

from polygon_utils import simplify_polygons
from stl_utils import export_stl

logger = logging.getLogger('main')
logging.basicConfig()


def create_region_puzzle(country_name: str, output_folder: str) -> None:
    boundary_polygons = pickle.load( open( "boundary_polygons.p", "rb" ) )
    simplified_polygons = simplify_polygons(boundary_polygons, county_names)
    # show_merged_stl(simplified_polygons)

    for i, polygon in enumerate(simplified_polygons):
        export_stl(polygon, county_names[i], output_folder)
        # Process(target=export_stl, args=(polygon, county_names[i], output_folder)).start()


if __name__ == "__main__":
    create_region_puzzle("Ireland", "output")