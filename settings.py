"""Project settings"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
# I use a layout similar to the one used by templates distributed along with AP's DataKit
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR_SRC = DATA_DIR / "source"
DATA_DIR_MANUAL = DATA_DIR / "manual"
DATA_DIR_PROCESSED = DATA_DIR / "processed"
DATA_DIR_PUBLIC = DATA_DIR / "public"