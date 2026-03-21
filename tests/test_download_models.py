import os
import unittest
from unittest.mock import patch

import pytest

from scripts.download_models import main


class TestDownloadModels(unittest.TestCase):
    @patch("scripts.download_models.verify_download", return_value=[])
    @patch("scripts.download_models.download_model")
    @patch("scripts.download_models.is_model_downloaded", return_value=True)
    def test_skips_download_when_model_already_present(
        self,
        _is_model_downloaded_mocked,
        download_model_mocked,
        _verify_download_mocked,
    ):
        main()

        download_model_mocked.assert_not_called()

    @patch("scripts.download_models.verify_download", return_value=[])
    @patch("scripts.download_models.download_model")
    @patch("scripts.download_models.is_model_downloaded", return_value=False)
    def test_downloads_when_model_missing(
        self,
        _is_model_downloaded_mocked,
        download_model_mocked,
        _verify_download_mocked,
    ):
        main()

        download_model_mocked.assert_called_once_with("sam2.1_hiera_base_plus_uint8")

    @patch("scripts.download_models.verify_download", return_value=["encoder.onnx"])
    @patch("scripts.download_models.download_model")
    @patch("scripts.download_models.is_model_downloaded", return_value=True)
    def test_exits_on_verification_failure(
        self,
        _is_model_downloaded_mocked,
        _download_model_mocked,
        _verify_download_mocked,
    ):
        with pytest.raises(SystemExit) as exc_info:
            main()

        self.assertEqual(exc_info.value.code, 1)

    @patch.dict(os.environ, {"MODEL_VARIANT": "sam2.1_hiera_tiny_uint8"})
    @patch("scripts.download_models.verify_download", return_value=[])
    @patch("scripts.download_models.download_model")
    @patch("scripts.download_models.is_model_downloaded", return_value=True)
    def test_respects_model_variant_env(
        self,
        is_model_downloaded_mocked,
        _download_model_mocked,
        verify_download_mocked,
    ):
        main()

        is_model_downloaded_mocked.assert_called_once_with("sam2.1_hiera_tiny_uint8")
        verify_download_mocked.assert_called_once_with("sam2.1_hiera_tiny_uint8")

    @patch("scripts.download_models.verify_download")
    @patch("scripts.download_models.download_model", side_effect=OSError("disk full"))
    @patch("scripts.download_models.is_model_downloaded", return_value=False)
    def test_raises_oserror_when_download_fails(
        self,
        _is_model_downloaded_mocked,
        _download_model_mocked,
        _verify_download_mocked,
    ):
        with pytest.raises(OSError):
            main()


if __name__ == "__main__":
    unittest.main()
