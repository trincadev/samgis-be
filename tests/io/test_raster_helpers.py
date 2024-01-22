import numpy as np
import unittest
from unittest.mock import patch

from samgis.io import raster_helpers
from samgis.utilities.utilities import hash_calculate


def get_three_channels(size=5, param1=1000, param2=3, param3=-88):
    arr_base = np.arange(size*size).reshape(size, size) / size**2
    channel_0 = arr_base * param1
    channel_1 = arr_base * param2
    channel_2 = arr_base * param3
    return channel_0, channel_1, channel_2


def helper_bell(size=10, param1=0.1, param2=2):
    x = np.linspace(-size, size, num=size**2)
    y = np.linspace(-size, size, num=size**2)
    x, y = np.meshgrid(x, y)
    return np.exp(-param1 * x ** param2 - param1 * y ** param2)


arr_5x5x5 = np.arange(125).reshape((5, 5, 5)) / 25
arr = np.arange(25).resize((5, 5))
channel0, channel1, channel2 = get_three_channels()
z = helper_bell()
slope_z_cellsize3, curvature_z_cellsize3 = raster_helpers.get_slope_curvature(z, slope_cellsize=3)


class Test(unittest.TestCase):

    def test_get_rgb_prediction_image_real(self):
        output = raster_helpers.get_rgb_prediction_image(z, slope_cellsize=61, invert_image=True)
        hash_output = hash_calculate(output)
        assert hash_output == b'QpQ9yxgCLw9cf3klNFKNFXIDHaSkuiZxkbpeQApR8pA='
        output = raster_helpers.get_rgb_prediction_image(z, slope_cellsize=61, invert_image=False)
        hash_output = hash_calculate(output)
        assert hash_output == b'Y+iXO9w/sKzNVOw2rBh2JrVGJUFRqaa8/0F9hpevmLs='

    @patch.object(raster_helpers, "get_slope_curvature")
    @patch.object(raster_helpers, "normalize_array_list")
    @patch.object(raster_helpers, "get_rgb_image")
    def test_get_rgb_prediction_image_mocked(self, get_rgb_image_mocked, normalize_array_list, get_slope_curvature):
        local_arr = np.array(z * 100, dtype=np.uint8)

        get_slope_curvature.return_value = slope_z_cellsize3, curvature_z_cellsize3
        normalize_array_list.side_effect = None
        get_rgb_image_mocked.return_value = np.bitwise_not(local_arr)
        output = raster_helpers.get_rgb_prediction_image(local_arr, slope_cellsize=61, invert_image=True)
        hash_output = hash_calculate(output)
        assert hash_output == b'BPIyVH64RgVunj42EuQAx4/v59Va8ZAjcMnuiGNqTT0='
        get_rgb_image_mocked.return_value = local_arr
        output = raster_helpers.get_rgb_prediction_image(local_arr, slope_cellsize=61, invert_image=False)
        hash_output = hash_calculate(output)
        assert hash_output == b'XX54sdLQQUrhkUHT6ikQZYSloMYDSfh/AGITDq6jnRM='

    @patch.object(raster_helpers, "get_slope_curvature")
    def test_get_rgb_prediction_image_value_error(self, get_slope_curvature):
        msg = "this is a value error"
        get_slope_curvature.side_effect = ValueError(msg)

        with self.assertRaises(ValueError):
            try:
                raster_helpers.get_rgb_prediction_image(arr, slope_cellsize=3)
            except ValueError as ve:
                self.assertEqual(str(ve), msg)
                raise ve

    def test_get_rgb_image(self):
        output = raster_helpers.get_rgb_image(channel0, channel1, channel2, invert_image=True)
        hash_output = hash_calculate(output)
        assert hash_output == b'YVnRWla5Ptfet6reSfM+OEIsGytLkeso6X+CRs34YHk='
        output = raster_helpers.get_rgb_image(channel0, channel1, channel2, invert_image=False)
        hash_output = hash_calculate(output)
        assert hash_output == b'LC/kIZGUZULSrwwSXCeP1My2spTZdW9D7LH+tltwERs='

    def test_get_rgb_image_value_error_1(self):
        with self.assertRaises(ValueError):
            try:
                raster_helpers.get_rgb_image(arr_5x5x5, arr_5x5x5, arr_5x5x5, invert_image=True)
            except ValueError as ve:
                self.assertEqual(f"arr_size, wrong type:{type(arr_5x5x5)} or arr_size:{arr_5x5x5.shape}.", str(ve))
                raise ve

    def test_get_rgb_image_value_error2(self):
        arr_0 = np.arange(25).reshape((5, 5))
        arr_1 = np.arange(4).reshape((2, 2))
        with self.assertRaises(ValueError):
            try:
                raster_helpers.get_rgb_image(arr_0, arr_1, channel2, invert_image=True)
            except ValueError as ve:
                self.assertEqual('could not broadcast input array from shape (2,2) into shape (5,5)', str(ve))
                raise ve

    def test_get_slope_curvature(self):
        slope_output, curvature_output = raster_helpers.get_slope_curvature(z, slope_cellsize=3)
        hash_curvature = hash_calculate(curvature_output)
        hash_slope = hash_calculate(slope_output)
        assert hash_curvature == b'LAL9JFOjJP9D6X4X3fVCpnitx9VPM9drS5YMHwMZ3iE='
        assert hash_slope == b'IYf6x4G0lmR47j6HRS5kUYWdtmimhLz2nak8py75nwc='

    def test_get_slope_curvature_value_error(self):
        from samgis.io import raster_helpers

        with self.assertRaises(ValueError):
            try:
                raster_helpers.get_slope_curvature(np.array(1), slope_cellsize=3)
            except ValueError as ve:
                self.assertEqual('not enough values to unpack (expected 2, got 0)', str(ve))
                raise ve

    def test_calculate_slope(self):
        slope_output = raster_helpers.calculate_slope(z, cell_size=3)
        hash_output = hash_calculate(slope_output)
        assert hash_output == b'IYf6x4G0lmR47j6HRS5kUYWdtmimhLz2nak8py75nwc='

    def test_calculate_slope_value_error(self):
        with self.assertRaises(ValueError):
            try:
                raster_helpers.calculate_slope(np.array(1), cell_size=3)
            except ValueError as ve:
                self.assertEqual('not enough values to unpack (expected 2, got 0)', str(ve))
                raise ve

    def test_normalize_array(self):
        def check_ndarrays_almost_equal(cls, arr1, arr2, places, check_type="float", check_ndiff=1):
            count_abs_diff = 0
            for list00, list01 in zip(arr1.tolist(), arr2.tolist()):
                for el00, el01 in zip(list00, list01):
                    ndiff = abs(el00 - el01)
                    if el00 != el01:
                        count_abs_diff += 1
                    if check_type == "float":
                        cls.assertAlmostEqual(el00, el01, places=places)
                    cls.assertTrue(ndiff < check_ndiff)
            print("count_abs_diff:", count_abs_diff)

        normalized_array = raster_helpers.normalize_array(z)
        hash_output = hash_calculate(normalized_array)
        assert hash_output == b'MPkQwiiQa5NxL7LDvCS9V143YUEJT/Qh1aNEKc/Ehvo='

        mult_variable = 3.423
        test_array_input = np.arange(256).reshape((16, 16))
        test_array_output = raster_helpers.normalize_array(test_array_input * mult_variable)
        check_ndarrays_almost_equal(self, test_array_output, test_array_input, places=8)

        test_array_output1 = raster_helpers.normalize_array(test_array_input * mult_variable, high=128, norm_type="int")
        o = np.arange(256).reshape((16, 16)) / 2
        expected_array_output1 = o.astype(int)
        check_ndarrays_almost_equal(
            self, test_array_output1, expected_array_output1, places=2, check_type="int", check_ndiff=2)

    @patch.object(np, "nanmin")
    @patch.object(np, "nanmax")
    def test_normalize_array_floating_point_error_mocked(self, nanmax_mocked, nanmin_mocked):
        nanmax_mocked.return_value = 100
        nanmin_mocked.return_value = 100

        with self.assertRaises(ValueError):
            try:
                raster_helpers.normalize_array(
                    np.arange(25).reshape((5, 5))
                )
            except ValueError as ve:
                self.assertEqual(
                    "normalize_array:::h_arr_max:100,h_min_arr:100,fe:divide by zero encountered in divide.",
                    str(ve)
                )
                raise ve

    @patch.object(np, "nanmin")
    @patch.object(np, "nanmax")
    def test_normalize_array_exception_error_mocked(self, nanmax_mocked, nanmin_mocked):
        nanmax_mocked.return_value = 100
        nanmin_mocked.return_value = np.NaN

        with self.assertRaises(ValueError):
            try:
                raster_helpers.normalize_array(
                    np.arange(25).reshape((5, 5))
                )
            except ValueError as ve:
                self.assertEqual("cannot convert float NaN to integer", str(ve))
                raise ve

    def test_normalize_array_value_error(self):
        with self.assertRaises(ValueError):
            try:
                raster_helpers.normalize_array(
                    np.zeros((5, 5))
                )
            except ValueError as ve:
                self.assertEqual(
                    "normalize_array::empty array '',h_min_arr:0.0,h_arr_max:0.0,h_diff:0.0, " 'dtype:float64.',
                    str(ve)
                )
                raise ve

    def test_normalize_array_list(self):
        normalized_array = raster_helpers.normalize_array_list([channel0, channel1, channel2])
        hash_output = hash_calculate(normalized_array)
        assert hash_output == b'+6IbhIpyb3vPElTgqqPkQdIR0umf4uFP2c7t5IaBVvI='

        test_norm_list_output2 = raster_helpers.normalize_array_list(
            [channel0, channel1, channel2], exaggerations_list=[2.0, 3.0, 5.0])
        hash_variable2 = hash_calculate(test_norm_list_output2)
        assert hash_variable2 == b'yYCYWCKO3i8NYsWk/wgYOzSRRLSLUprEs7mChJkdL+A='

    def test_normalize_array_list_value_error(self):
        with self.assertRaises(ValueError):
            try:
                raster_helpers.normalize_array_list([])
            except ValueError as ve:
                self.assertEqual("input list can't be empty:[].", str(ve))
                raise ve

    def test_check_empty_array(self):
        a = np.zeros((10, 10))
        b = np.ones((10, 10))
        c = np.ones((10, 10)) * 2
        d = np.zeros((10, 10))
        d[1, 1] = np.nan
        e = np.ones((10, 10)) * 3
        e[1, 1] = np.nan

        self.assertTrue(raster_helpers.check_empty_array(a, 999))
        self.assertTrue(raster_helpers.check_empty_array(b, 0))
        self.assertTrue(raster_helpers.check_empty_array(c, 2))
        self.assertTrue(raster_helpers.check_empty_array(d, 0))
        self.assertTrue(raster_helpers.check_empty_array(e, 3))
        self.assertFalse(raster_helpers.check_empty_array(z, 3))

    def test_get_nextzen_terrain_rgb_formula(self):
        output = raster_helpers.get_nextzen_terrain_rgb_formula(channel0, channel1, channel2)
        hash_output = hash_calculate(output)
        assert hash_output == b'3KJ81YKmQRdccRZARbByfwo1iMVLj8xxz9mfsWki/qA='

    def test_get_mapbox__terrain_rgb_formula(self):
        output = raster_helpers.get_mapbox__terrain_rgb_formula(channel0, channel1, channel2)
        hash_output = hash_calculate(output)
        assert hash_output == b'RU7CcoKoR3Fkh5LE+m48DHRVUy/vGq6UgfOFUMXx07M='

    def test_get_raster_terrain_rgb_like(self):
        from samgis.utilities.type_hints import XYZTerrainProvidersNames

        arr_input = raster_helpers.get_rgb_image(channel0, channel1, channel2, invert_image=True)
        output_nextzen = raster_helpers.get_raster_terrain_rgb_like(
            arr_input, XYZTerrainProvidersNames.NEXTZEN_TERRAIN_TILES_NAME)
        hash_nextzen = hash_calculate(output_nextzen)
        assert hash_nextzen == b'+o2OTJliJkkBoqiAIGnhJ4s0xoLQ4MxHOvevLhNxysE='
        output_mapbox = raster_helpers.get_raster_terrain_rgb_like(
            arr_input, XYZTerrainProvidersNames.MAPBOX_TERRAIN_TILES_NAME)
        hash_mapbox = hash_calculate(output_mapbox)
        assert hash_mapbox == b'zWmekyKrpnmHnuDACnveCJl+o4GuhtHJmGlRDVwsce4='
