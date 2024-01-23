# About this project

SamGIS is an attempt to perform [machine learning](https://developer.ibm.com/learningpaths/get-started-artificial-intelligence/ai-basics/ai-beginners-guide) [instance segmentation](https://en.wikipedia.org/wiki/Image_segmentation) on [geospatial data](https://en.wikipedia.org/wiki/Geographic_data_and_information) even without the use of dedicated graphics cards.
The user interact on a [leaflet](https://leafletjs.com) webmap choosing areas to recognize and a backend responds with a [geojson](https://it.wikipedia.org/wiki/GeoJSON) containing one or more recognized polygons within the initial webmap.

The backend perform machine learning inference using a [Segment Anything](https://segment-anything.com) model and [ONNXRuntime](https://onnxruntime.ai) as runtime.

Check about implementation details on my [blog](https://trinca.tornidor.com/projects/samgis-segment-anything-applied-to-GIS).

# Self-hosted demo

You can visit my self-hosted demo [here](https://ml-trinca.tornidor.com).
Since this demo uses a python container backend hosted on my AWS account I keep it under authentication to prevent abuses.
[Here](https://docs.ml-trinca.tornidor.com/openapi) the OpenAPI swagger documentation.

# HuggingFace Space demo

I added also a demo on this [HuggingFace Space](https://huggingface.co/spaces/aletrn/samgis). It's
possible to find [here](https://aletrn-samgis.hf.space/) the direct space url and 
[here](https://aletrn-samgis.hf.space/docs#/) the OpenAPI swagger documentation.
