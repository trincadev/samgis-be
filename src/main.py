from typing import Dict

from geojson_pydantic import Feature, Polygon, FeatureCollection
from pydantic import BaseModel

g1 = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [13.1, 52.46385],
                    [13.42786, 52.6],
                    [13.2, 52.5],
                    [13.38272, 52.4],
                    [13.43, 52.46385],
                    [13.1, 52.46385]
                ]
            ],
        },
        "properties": {
            "name": "uno",
        },
    }, {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [13.77, 52.8],
                    [13.88, 52.77],
                    [13.99, 52.66],
                    [13.11, 52.55],
                    [13.33, 52.44],
                    [13.77, 52.8]
                ]
            ],
        },
        "properties": {
            "name": "due",
        },
    }]
}

PolygonFeatureCollectionModel = FeatureCollection[Feature[Polygon, Dict]]

if __name__ == '__main__':
    feat = PolygonFeatureCollectionModel(**g1)
    print(feat)
    print("feat")
    """
    
    point:  {"lat":12.425847783029134,"lng":53.887939453125} 
    map:ne:{"lat":17.895114303749143,"lng":58.27148437500001} sw:{"lat":0.6591651462894632,"lng":34.01367187500001}.
    """
