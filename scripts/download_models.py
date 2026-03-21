"""CLI entry point to download SAM model weights via the samgis_core registry."""

import os
import sys

from samgis_core.prediction_api.model_downloader import download_model
from samgis_core.prediction_api.model_registry import (
    is_model_downloaded,
    verify_download,
)


def main() -> None:
    variant = os.getenv("MODEL_VARIANT", "sam2.1_hiera_base_plus_uint8")

    if is_model_downloaded(variant):
        print(f"Model '{variant}' already present, verifying checksums...")
    else:
        print(f"Downloading model '{variant}'...")
        download_model(variant)  # raises OSError on SHA-256 mismatch internally

    failures = verify_download(variant)
    if failures:
        print(
            f"SHA-256 verification FAILED for: {', '.join(failures)}", file=sys.stderr
        )
        sys.exit(1)
    print(f"Model '{variant}' ready, SHA-256 verified.")


if __name__ == "__main__":
    main()
