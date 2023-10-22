# Press the green button in the gutter to run the script.
import json

from src import app_logger
from src.utilities.constants import ROOT
from src.utilities.type_hints import input_floatlist, input_floatlist2


def base_predict(
        bbox: input_floatlist, point_coords: input_floatlist2, point_crs: str = "EPSG:4326", zoom: float = 16, model_name: str = "vit_h", root_folder: str = ROOT
) -> str:
    from samgeo import SamGeo, tms_to_geotiff

    image = f"{root_folder}/satellite.tif"
    app_logger.info(f"start tms_to_geotiff using bbox:{bbox}, type:{type(bbox)}.")
    for coord in bbox:
        app_logger.info(f"coord:{coord}, type:{type(coord)}.")
    # bbox: image input coordinate
    tms_to_geotiff(output=image, bbox=bbox, zoom=zoom, source="Satellite", overwrite=True)

    app_logger.info(f"geotiff created, start to initialize samgeo instance (read model {model_name} from {root_folder})...")

    predictor = SamGeo(
        model_type=model_name,
        checkpoint_dir=root_folder,
        automatic=False,
        sam_kwargs=None,
    )
    app_logger.info(f"initialized samgeo instance, start to set_image {image}...")
    predictor.set_image(image)
    output_name = f"{root_folder}/output.tif"

    app_logger.info(f"done set_image, start prediction...")
    predictor.predict(point_coords, point_labels=len(point_coords), point_crs=point_crs, output=output_name)

    app_logger.info(f"done prediction, start tiff to geojson conversion...")

    # geotiff to geojson
    vector = f"{root_folder}/feats.geojson"
    predictor.tiff_to_geojson(output_name, vector, bidx=1)
    app_logger.info(f"start reading geojson...")

    with open(vector) as out_gdf:
        out_gdf_str = out_gdf.read()
        out_gdf_json = json.loads(out_gdf_str)
        app_logger.info(f"geojson string output length:{len(out_gdf_str)}.")
        return out_gdf_json
