# Press the green button in the gutter to run the script.
import json

from src.utilities.constants import ROOT
from src.utilities.utilities import setup_logging


local_logger = setup_logging()


def base_predict(bbox, point_coords, point_crs="EPSG:4326", zoom=16, model_name:str="vit_h", root_folder:str=ROOT) -> str:
    from samgeo import SamGeo, tms_to_geotiff

    image = f"{root_folder}/satellite.tif"
    local_logger.info("start tms_to_geotiff")
    # bbox: image input coordinate
    tms_to_geotiff(output=image, bbox=bbox, zoom=zoom, source="Satellite", overwrite=True)

    local_logger.info(f"geotiff created, start to initialize samgeo instance (read model {model_name} from {root_folder})...")
    predictor = SamGeo(
        model_type=model_name,
        checkpoint_dir=root_folder,
        automatic=False,
        sam_kwargs=None,
    )
    local_logger.info(f"initialized samgeo instance, start to set_image {image}...")
    predictor.set_image(image)
    output_name = f"{root_folder}/output.tif"
    
    local_logger.info(f"done set_image, start prediction...")
    predictor.predict(point_coords, point_labels=len(point_coords), point_crs=point_crs, output=output_name)
    
    local_logger.info(f"done prediction, start tiff to geojson conversion...")

    # geotiff to geojson
    vector = f"{root_folder}/feats.geojson"
    predictor.tiff_to_geojson(output_name, vector, bidx=1)
    local_logger.info(f"start reading geojson...")

    with open(vector) as out_gdf:
        out_gdf_str = json.load(out_gdf)
        local_logger.info(f"number of fields in geojson output:{len(out_gdf_str)}.")
        return out_gdf_str
