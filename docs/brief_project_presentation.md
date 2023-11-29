# About this project

SamGIS is an attempt to perform [machine learning](https://developer.ibm.com/learningpaths/get-started-artificial-intelligence/ai-basics/ai-beginners-guide) [instance segmentation](https://en.wikipedia.org/wiki/Image_segmentation) on [geospatial data](https://en.wikipedia.org/wiki/Geographic_data_and_information) even without the use of dedicated graphics cards.
The user interact on a [leaflet](https://leafletjs.com) webmap choosing areas to recognize and a backend responds with a [geojson](https://it.wikipedia.org/wiki/GeoJSON) containing one or more recognized polygons within the initial webmap.

The backend perform machine learning inference using a [Segment Anything](https://segment-anything.com) model and [ONNXRuntime](https://onnxruntime.ai) as runtime.

Check about implementation details on my [blog](https://trinca.tornidor.com/projects/samgis-segment-anything-applied-to-GIS).
