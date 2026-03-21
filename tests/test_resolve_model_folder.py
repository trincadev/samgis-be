import os
import unittest
from pathlib import Path
from unittest.mock import patch


class TestResolveModelFolder(unittest.TestCase):
    @patch.dict(os.environ, {"MODEL_FOLDER": "/tmp/custom_models"})
    @patch("samgis_core.prediction_api.model_registry.get_model_dir")
    def test_model_folder_env_override(self, get_model_dir_mocked):
        import app as app_module

        result = app_module.resolve_model_folder()

        get_model_dir_mocked.assert_not_called()
        self.assertEqual(result, Path("/tmp/custom_models"))

    @patch.dict(
        os.environ,
        {"MODEL_VARIANT": "sam2.1_hiera_tiny_uint8"},
        clear=False,
    )
    @patch("samgis_core.prediction_api.model_registry.get_model_dir")
    def test_model_variant_env_uses_registry(self, get_model_dir_mocked):
        get_model_dir_mocked.return_value = Path("/mock/tiny")

        # Ensure MODEL_FOLDER is absent
        os.environ.pop("MODEL_FOLDER", None)

        import app as app_module

        get_model_dir_mocked.reset_mock()
        result = app_module.resolve_model_folder()

        get_model_dir_mocked.assert_called_once_with("sam2.1_hiera_tiny_uint8")
        self.assertEqual(result, Path("/mock/tiny"))

    @patch("samgis_core.prediction_api.model_registry.get_model_dir")
    def test_default_variant_when_no_env_vars(self, get_model_dir_mocked):
        get_model_dir_mocked.return_value = Path("/mock/default")

        os.environ.pop("MODEL_FOLDER", None)
        os.environ.pop("MODEL_VARIANT", None)

        import app as app_module

        get_model_dir_mocked.reset_mock()
        result = app_module.resolve_model_folder()

        get_model_dir_mocked.assert_called_once_with("sam2.1_hiera_base_plus_uint8")
        self.assertEqual(result, Path("/mock/default"))

    @patch.dict(os.environ, {"MODEL_FOLDER": ""})
    @patch("samgis_core.prediction_api.model_registry.get_model_dir")
    def test_empty_string_model_folder(self, get_model_dir_mocked):
        import app as app_module

        result = app_module.resolve_model_folder()

        get_model_dir_mocked.assert_not_called()
        self.assertEqual(result, Path(""))


if __name__ == "__main__":
    unittest.main()
