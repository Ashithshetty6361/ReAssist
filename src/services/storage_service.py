"""
ReAssist — Storage Service Layer
Encapsulates file storage operations, SHA-256 deduplication, and presigned URLs.
"""

import hashlib
from typing import Union, BinaryIO
from src.core.storage import get_storage_provider, StorageProvider


class StorageService:
    """Service for managing document files, PDFs, exports, and execution artifacts."""

    def __init__(self, provider: StorageProvider | None = None):
        self.provider = provider or get_storage_provider()

    @staticmethod
    def calculate_sha256(data: Union[bytes, str]) -> str:
        """Calculate SHA-256 hash for document deduplication."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def store_document(self, content: bytes, filename: str, workspace_id: str) -> dict:
        """
        Store a document file with SHA-256 deduplication.
        Returns metadata dict with path, hash, and accessible url.
        """
        file_hash = self.calculate_sha256(content)
        path = f"uploads/ws_{workspace_id}/{file_hash}_{filename}"
        saved_ref = self.provider.save_file(content, path)
        url = self.provider.get_url(saved_ref)

        return {
            "blob_url": saved_ref,
            "accessible_url": url,
            "file_hash": file_hash,
            "filename": filename,
            "size_bytes": len(content),
        }

    def store_artifact(self, content: Union[str, bytes], path: str, content_type: str = "application/json") -> str:
        """Store an execution result or exported dossier."""
        return self.provider.save_file(content, path, content_type=content_type)

    def retrieve_artifact(self, path: str) -> bytes:
        """Retrieve stored artifact content."""
        return self.provider.read_file(path)

    def get_accessible_url(self, path: str, expires_in_seconds: int = 3600) -> str:
        """Get an accessible URL (direct or presigned)."""
        return self.provider.get_url(path, expires_in_seconds=expires_in_seconds)


_storage_service = None

def get_storage_service() -> StorageService:
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
