# Press the green button in the gutter to run the script.
import json

from src import app_logger
from src.utilities.constants import ROOT
from src.utilities.type_hints import input_floatlist, input_floatlist2


def base_predict(
        bbox: input_floatlist, point_coords: input_floatlist2, point_crs: str = "EPSG:4326", zoom: float = 16, model_name: str = "vit_h", root_folder: str = ROOT
) -> str:
    import tempfile
    from samgeo import SamGeo, tms_to_geotiff

    with tempfile.NamedTemporaryFile(prefix="satellite_", suffix=".tif", dir=root_folder) as image_input_tmp:
        app_logger.info(f"start tms_to_geotiff using bbox:{bbox}, type:{type(bbox)}, download image to {image_input_tmp.name} ...")
        for coord in bbox:
            app_logger.info(f"coord:{coord}, type:{type(coord)}.")

        # bbox: image input coordinate
        tms_to_geotiff(output=image_input_tmp.name, bbox=bbox, zoom=zoom, source="Satellite", overwrite=True)
        app_logger.info(f"geotiff created, start to initialize samgeo instance (read model {model_name} from {root_folder})...")

        predictor = SamGeo(
            model_type=model_name,
            checkpoint_dir=root_folder,
            automatic=False,
            sam_kwargs=None,
        )
        app_logger.info(f"initialized samgeo instance, start to use SamGeo.set_image({image_input_tmp.name})...")
        predictor.set_image(image_input_tmp.name)

        with tempfile.NamedTemporaryFile(prefix="output_", suffix=".tif", dir=root_folder) as image_output_tmp:
            app_logger.info(f"done set_image, start prediction using {image_output_tmp.name} as output...")
            predictor.predict(point_coords, point_labels=len(point_coords), point_crs=point_crs, output=image_output_tmp.name)

            # geotiff to geojson
            with tempfile.NamedTemporaryFile(prefix="feats_", suffix=".geojson", dir=root_folder) as vector_tmp:
                app_logger.info(f"done prediction, start conversion SamGeo.tiff_to_geojson({image_output_tmp.name}) => {vector_tmp.name}.")
                predictor.tiff_to_geojson(image_output_tmp.name, vector_tmp.name, bidx=1)

                app_logger.info(f"start reading geojson {vector_tmp.name}...")
                with open(vector_tmp.name) as out_gdf:
                    out_gdf_str = out_gdf.read()
                    out_gdf_json = json.loads(out_gdf_str)
                    app_logger.info(f"geojson {vector_tmp.name} string has length: {len(out_gdf_str)}.")
                    return out_gdf_json
