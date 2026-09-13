"""Extract sprite thumbnails from pokemon-images/thumbnails.zip."""

import zipfile
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent
ZIP_PATH = BASE_PATH / "pokemon-images/thumbnails.zip"
THUMBNAILS_PATH = BASE_PATH / "pokemon-images/thumbnails"


def main() -> None:
    if (THUMBNAILS_PATH / "0001.png").exists():
        print("Sprites already extracted.")
        return
    if not ZIP_PATH.exists():
        print(f"Missing {ZIP_PATH}")
        raise SystemExit(1)
    with zipfile.ZipFile(ZIP_PATH) as archive:
        archive.extractall(ZIP_PATH.parent)
    count = len(list(THUMBNAILS_PATH.glob("*.png")))
    print(f"Extracted {count} sprites to {THUMBNAILS_PATH}")


if __name__ == "__main__":
    main()
