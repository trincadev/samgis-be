from unittest import TestCase


class Test(TestCase):
    def test_get_latlng2pixel_projection(self):
        from src.io.coordinates_pixel_conversion import get_latlng2pixel_projection

        # europa
        output = get_latlng2pixel_projection({"lat": 55.82499925397549, "lng": 30.55813798557972})
        assert output == {"x": 149.73023145641224, "y": 79.93873304907419}

        # nord america
        output = get_latlng2pixel_projection({"lat": 55.73904872165355, "lng": -88.38855385872797})
        assert output == {"x": 65.14591725601566, "y": 80.04742192145312}

        # sud america
        output = get_latlng2pixel_projection({"lat": -28.07197941598981, "lng": -81.47485480086976})
        assert output == {"x": 70.06232547493705, "y": 148.8124992861222}

        # tasmania
        output = get_latlng2pixel_projection({"lat": -42.10127784960304, "lng": 147.42782020699818})
        assert output == {"x": 232.8375610360876, "y": 161.06542832667049}

    def test_get_point_latlng_to_pixel_coordinates(self):
        from src.io.coordinates_pixel_conversion import get_point_latlng_to_pixel_coordinates

        # europa
        output = get_point_latlng_to_pixel_coordinates(
            latlng={"lat": 38.26837671763853, "lng": 13.640947603420843},
            zoom=10
        )
        assert output == {"x": 141005, "y": 100867}

        # nord america
        output = get_point_latlng_to_pixel_coordinates(
            latlng={"lat": 49.582282020151446, "lng": -114.91703409765535},
            zoom=7
        )
        assert output == {"x": 5923, "y": 11171}

        # sud america
        output = get_point_latlng_to_pixel_coordinates(
            latlng={"lat": -32.52828619080139, "lng": -73.03714474717113}, zoom=7
        )
        assert output == {"x": 9735, "y": 19517}

        # tasmania
        output = get_point_latlng_to_pixel_coordinates(
            latlng={"lat": -52.32191088594772, "lng": 65.30273437500001}, zoom=4
        )
        assert output == {"x": 2791, "y": 2749}

    # def test_get_latlng_to_pixel_coordinates(self):
    #     self.fail()
    #
    # def test_pixel_coordinate(self):
    #     self.fail()
