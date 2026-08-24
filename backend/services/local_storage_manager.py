"""
Local Storage Manager (ADR-008)

FileStorage adapter writing uploads to a local folder, served back over HTTP
by the StaticFiles mount in main.py (the frontend PDF viewer and the OCR
client both consume the returned URL).
"""

import logging
from pathlib import Path
from typing import Optional

from config.settings import settings

logger = logging.getLogger(__name__)

# storage_path is server-generated (uuid + extension), but the extension comes
# from the client filename — whitelist it (MIME is validated separately at upload)
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


class LocalStorageManager:
    """FileStorage adapter backed by a local directory."""

    def __init__(self, upload_dir: str):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def upload_file(self, file_content: bytes, storage_path: str) -> str:
        extension = Path(storage_path).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file extension: {extension}")
        target = self.upload_dir / storage_path
        target.write_bytes(file_content)
        logger.info(f"Stored file locally: {target}")
        return f"{settings.PUBLIC_BASE_URL}/api/v1/files/{storage_path}"

    async def delete_file(self, storage_path: Optional[str]) -> None:
        if not storage_path:
            return
        try:
            (self.upload_dir / storage_path).unlink(missing_ok=True)
            logger.info(f"Deleted local file: {storage_path}")
        except Exception as e:
            logger.warning(f"Failed to delete local file {storage_path}: {e}")

    async def delete_file_with_retry(self, storage_path: str, max_retries: int = 3) -> None:
        # Local unlink does not transiently fail; kept for FileStorage parity
        (self.upload_dir / storage_path).unlink(missing_ok=True)
        logger.info(f"Deleted local file: {storage_path}")
