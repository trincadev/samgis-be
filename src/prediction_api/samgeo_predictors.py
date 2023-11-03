# Press the green button in the gutter to run the script.
import json
import os

from src import app_logger
from src.utilities.constants import ROOT, MODEL_NAME, ZOOM, SOURCE_TYPE
from src.utilities.type_hints import input_floatlist
from src.utilities.utilities import get_system_info


def samgeo_fast_predict(
        bbox: input_floatlist, zoom: float = ZOOM, model_name: str = MODEL_NAME, root_folder: str = ROOT, source_type: str = SOURCE_TYPE, crs="EPSG:4326"
) -> dict:
    import tempfile
    from samgeo import tms_to_geotiff
    from samgeo.fast_sam import SamGeo

    try:
        os.environ['MPLCONFIGDIR'] = root_folder
        get_system_info()
    except Exception as e:
        app_logger.error(f"Error while setting 'MPLCONFIGDIR':{e}.")

    with tempfile.NamedTemporaryFile(prefix=f"{source_type}_", suffix=".tif", dir=root_folder) as image_input_tmp:
        app_logger.info(f"start tms_to_geotiff using bbox:{bbox}, type:{type(bbox)}, download image to {image_input_tmp.name} ...")
        for coord in bbox:
            app_logger.info(f"coord:{coord}, type:{type(coord)}.")

        # bbox: image input coordinate
        tms_to_geotiff(output=image_input_tmp.name, bbox=bbox, zoom=zoom, source=source_type, overwrite=True, crs=crs)
        app_logger.info(f"geotiff created, start to initialize SamGeo instance (read model {model_name} from {root_folder})...")

        predictor = SamGeo(
            model_type=model_name,
            checkpoint_dir=root_folder,
            automatic=False,
            sam_kwargs=None,
        )
        app_logger.info(f"initialized SamGeo instance, start to use SamGeo.set_image({image_input_tmp.name})...")
        predictor.set_image(image_input_tmp.name)

        with tempfile.NamedTemporaryFile(prefix="output_", suffix=".tif", dir=root_folder) as image_output_tmp:
            app_logger.info(f"done set_image, start prediction using {image_output_tmp.name} as output...")
            predictor.everything_prompt(output=image_output_tmp.name)

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
