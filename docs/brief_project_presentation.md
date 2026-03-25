# About this project

SamGIS is an attempt to perform [machine learning](https://developer.ibm.com/learningpaths/get-started-artificial-intelligence/ai-basics/ai-beginners-guide) [instance segmentation](https://en.wikipedia.org/wiki/Image_segmentation) on [geospatial data](https://en.wikipedia.org/wiki/Geographic_data_and_information) even without the use of dedicated graphics cards.
The user interact on a [leaflet](https://leafletjs.com) webmap choosing areas to recognize and a backend responds with a [geojson](https://it.wikipedia.org/wiki/GeoJSON) containing one or more recognized polygons within the initial webmap.

The backend perform machine learning inference using a [Segment Anything Model 2 (SAM2)](https://github.com/facebookresearch/sam2) and [ONNXRuntime](https://onnxruntime.ai) as runtime.

Check about implementation details on my [blog](https://trinca.tornidor.com/projects/samgis-segment-anything-applied-to-GIS).

## Demo

A live demo is available on [HuggingFace Spaces](https://huggingface.co/spaces/aletrn/samgis).
The direct space URL is [here](https://aletrn-samgis.hf.space/) and the OpenAPI swagger documentation [here](https://aletrn-samgis.hf.space/docs#/).

A [QGIS plugin](https://plugins.qgis.org/plugins/samgis/) is also available for desktop GIS users ([project page](https://trinca.tornidor.com/projects/samgis-qgis-plugin)).
