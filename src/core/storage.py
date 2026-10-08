"""
ReAssist — Pluggable Storage Abstraction Layer

Supports multiple storage backends:
  - LocalStorageProvider: Stores documents and execution artifacts on the local filesystem.
  - S3StorageProvider: Stores documents and artifacts in Amazon S3 buckets via boto3.

Configured via STORAGE_BACKEND env var (default: "local").
"""

import os
import io
import shutil
from abc import ABC, abstractmethod
from typing import Optional, Union, BinaryIO


class StorageProvider(ABC):
    """Abstract interface for file and artifact storage."""

    @abstractmethod
    def save_file(self, file_data: Union[bytes, BinaryIO, str], path: str, content_type: str = "application/octet-stream") -> str:
        """Save data to storage and return accessible reference URI."""
        pass

    @abstractmethod
    def read_file(self, path: str) -> bytes:
        """Read data from storage as bytes."""
        pass

    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """Check if file exists at path."""
        pass

    @abstractmethod
    def get_url(self, path: str, expires_in_seconds: int = 3600) -> str:
        """Get an accessible URL (direct local path or presigned S3 URL)."""
        pass

    @abstractmethod
    def delete_file(self, path: str) -> bool:
        """Delete file at path."""
        pass


class LocalStorageProvider(StorageProvider):
    """Local filesystem storage provider."""

    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _resolve_path(self, path: str) -> str:
        if os.path.isabs(path):
            return path
        norm = os.path.normpath(path)
        base_norm = os.path.normpath(self.base_dir)
        if norm == base_norm or norm.startswith(base_norm + os.sep) or norm.startswith(self.base_dir + "/"):
            return norm
        return os.path.join(self.base_dir, path)

    def save_file(self, file_data: Union[bytes, BinaryIO, str], path: str, content_type: str = "application/octet-stream") -> str:
        full_path = self._resolve_path(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        if isinstance(file_data, str):
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(file_data)
        elif isinstance(file_data, bytes):
            with open(full_path, "wb") as f:
                f.write(file_data)
        else:
            with open(full_path, "wb") as f:
                shutil.copyfileobj(file_data, f)
        return full_path

    def read_file(self, path: str) -> bytes:
        full_path = self._resolve_path(path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found at {full_path}")
        with open(full_path, "rb") as f:
            return f.read()

    def file_exists(self, path: str) -> bool:
        return os.path.exists(self._resolve_path(path))

    def get_url(self, path: str, expires_in_seconds: int = 3600) -> str:
        return self._resolve_path(path)

    def delete_file(self, path: str) -> bool:
        full_path = self._resolve_path(path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False


class S3StorageProvider(StorageProvider):
    """AWS S3 object storage provider with fallback support."""

    def __init__(self, bucket_name: Optional[str] = None, region_name: Optional[str] = None):
        try:
            import boto3
        except ImportError:
            raise ImportError("boto3 is required for S3StorageProvider. Run: pip install boto3")

        self.bucket_name = bucket_name or os.getenv("S3_BUCKET_NAME", "reassist-storage")
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.s3_client = boto3.client(
            "s3",
            region_name=self.region_name,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID") or None,
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY") or None,
            aws_session_token=os.getenv("AWS_SESSION_TOKEN") or None,
        )

    def save_file(self, file_data: Union[bytes, BinaryIO, str], path: str, content_type: str = "application/octet-stream") -> str:
        s3_key = path.lstrip("/")
        if isinstance(file_data, str):
            body = file_data.encode("utf-8")
        elif isinstance(file_data, bytes):
            body = file_data
        else:
            body = file_data.read()

        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=body,
            ContentType=content_type
        )
        return f"s3://{self.bucket_name}/{s3_key}"

    def read_file(self, path: str) -> bytes:
        s3_key = path.replace(f"s3://{self.bucket_name}/", "").lstrip("/")
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
        return response["Body"].read()

    def file_exists(self, path: str) -> bool:
        s3_key = path.replace(f"s3://{self.bucket_name}/", "").lstrip("/")
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except Exception:
            return False

    def get_url(self, path: str, expires_in_seconds: int = 3600) -> str:
        s3_key = path.replace(f"s3://{self.bucket_name}/", "").lstrip("/")
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expires_in_seconds
            )
            return url
        except Exception:
            return f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{s3_key}"

    def delete_file(self, path: str) -> bool:
        s3_key = path.replace(f"s3://{self.bucket_name}/", "").lstrip("/")
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except Exception:
            return False


def get_storage_provider() -> StorageProvider:
    """Factory to return configured storage provider."""
    backend = os.getenv("STORAGE_BACKEND", "local").lower().strip()
    if backend in ("s3", "aws_s3", "aws"):
        try:
            return S3StorageProvider()
        except Exception as e:
            # Graceful fallback to local if S3/boto3 is not configured
            print(f"[Storage] Warning: Falling back to LocalStorageProvider: {e}")
            return LocalStorageProvider()
    return LocalStorageProvider()
