from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)


class CloudProvider(Enum):
    S3 = "s3"
    GCS = "gcs"


@dataclass
class CloudStorageConfig:
    provider: CloudProvider = CloudProvider.S3
    bucket: str = "gli-flow-runs"
    prefix: str = "runs"
    region: str = "us-east-1"
    credentials_file: str = ""


class CloudStorageManager:

    def __init__(self, config: CloudStorageConfig):
        self.config = config

    def upload_run(self, run_dir: str, run_id: str = "") -> str:
        run_id = run_id or Path(run_dir).name
        dest_key = f"{self.config.prefix}/{run_id}"

        if self.config.provider == CloudProvider.S3:
            return self._upload_s3(run_dir, dest_key)
        elif self.config.provider == CloudProvider.GCS:
            return self._upload_gcs(run_dir, dest_key)
        return ""

    def download_run(self, run_id: str, dest_dir: str) -> str:
        src_key = f"{self.config.prefix}/{run_id}"

        if self.config.provider == CloudProvider.S3:
            return self._download_s3(src_key, dest_dir)
        elif self.config.provider == CloudProvider.GCS:
            return self._download_gcs(src_key, dest_dir)
        return ""

    def list_runs(self) -> list[str]:
        if self.config.provider == CloudProvider.S3:
            return self._list_s3()
        elif self.config.provider == CloudProvider.GCS:
            return self._list_gcs()
        return []

    def _get_s3_client(self):
        import boto3
        kwargs = {"region_name": self.config.region}
        if self.config.credentials_file:
            import configparser
            cp = configparser.ConfigParser()
            cp.read(self.config.credentials_file)
            if "default" in cp:
                kwargs["aws_access_key_id"] = cp["default"].get("aws_access_key_id", "")
                kwargs["aws_secret_access_key"] = cp["default"].get("aws_secret_access_key", "")
        return boto3.client("s3", **kwargs)

    def _upload_s3(self, run_dir: str, dest_key: str) -> str:
        try:
            client = self._get_s3_client()
            root = Path(run_dir)
            uploaded = 0
            for f in root.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(root)
                    client.upload_file(str(f), self.config.bucket, f"{dest_key}/{rel}")
                    uploaded += 1
            logger.info("Uploaded %d files to s3://%s/%s", uploaded, self.config.bucket, dest_key)
            return f"s3://{self.config.bucket}/{dest_key}"
        except ImportError:
            logger.error("boto3 not installed — install with: pip install gli-flow[cloud]")
            return ""
        except Exception as e:
            logger.error("S3 upload failed: %s", e)
            return ""

    def _download_s3(self, src_key: str, dest_dir: str) -> str:
        try:
            client = self._get_s3_client()
            paginator = client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.config.bucket, Prefix=src_key)
            downloaded = 0
            for page in pages:
                for obj in page.get("Contents", []):
                    rel = Path(obj["Key"]).relative_to(src_key)
                    dest = Path(dest_dir) / rel
                    resolved = dest.resolve()
                    dest_root = Path(dest_dir).resolve()
                    if not str(resolved).startswith(str(dest_root)):
                        raise ValueError(f"Path traversal detected: {obj['Key']} resolves outside {dest_dir}")
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    client.download_file(self.config.bucket, obj["Key"], str(dest))
                    downloaded += 1
            logger.info("Downloaded %d files from s3://%s/%s", downloaded, self.config.bucket, src_key)
            return dest_dir
        except ImportError:
            logger.error("boto3 not installed")
            return ""
        except Exception as e:
            logger.error("S3 download failed: %s", e)
            return ""

    def _list_s3(self) -> list[str]:
        try:
            client = self._get_s3_client()
            paginator = client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.config.bucket, Prefix=self.config.prefix)
            runs = set()
            for page in pages:
                for obj in page.get("Contents", []):
                    parts = obj["Key"].split("/")
                    if len(parts) > 1:
                        runs.add(parts[1])
            return sorted(runs)
        except ImportError:
            logger.error("boto3 not installed")
            return []
        except Exception as e:
            logger.error("S3 list failed: %s", e)
            return []

    def _get_gcs_client(self):
        from google.cloud import storage
        if self.config.credentials_file:
            return storage.Client.from_service_account_json(self.config.credentials_file)
        return storage.Client()

    def _upload_gcs(self, run_dir: str, dest_key: str) -> str:
        try:
            client = self._get_gcs_client()
            bucket = client.bucket(self.config.bucket)
            root = Path(run_dir)
            uploaded = 0
            for f in root.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(root)
                    blob = bucket.blob(f"{dest_key}/{rel}")
                    blob.upload_from_filename(str(f))
                    uploaded += 1
            logger.info("Uploaded %d files to gs://%s/%s", uploaded, self.config.bucket, dest_key)
            return f"gs://{self.config.bucket}/{dest_key}"
        except ImportError:
            logger.error("google-cloud-storage not installed — install with: pip install gli-flow[cloud]")
            return ""
        except Exception as e:
            logger.error("GCS upload failed: %s", e)
            return ""

    def _download_gcs(self, src_key: str, dest_dir: str) -> str:
        try:
            client = self._get_gcs_client()
            bucket = client.bucket(self.config.bucket)
            blobs = bucket.list_blobs(prefix=src_key)
            downloaded = 0
            for blob in blobs:
                rel = Path(blob.name).relative_to(src_key)
                dest = Path(dest_dir) / rel
                resolved = dest.resolve()
                dest_root = Path(dest_dir).resolve()
                if not str(resolved).startswith(str(dest_root)):
                    raise ValueError(f"Path traversal detected: {blob.name} resolves outside {dest_dir}")
                dest.parent.mkdir(parents=True, exist_ok=True)
                blob.download_to_filename(str(dest))
                downloaded += 1
            logger.info("Downloaded %d files from gs://%s/%s", downloaded, self.config.bucket, src_key)
            return dest_dir
        except ImportError:
            logger.error("google-cloud-storage not installed")
            return ""
        except Exception as e:
            logger.error("GCS download failed: %s", e)
            return ""

    def _list_gcs(self) -> list[str]:
        try:
            client = self._get_gcs_client()
            bucket = client.bucket(self.config.bucket)
            blobs = bucket.list_blobs(prefix=self.config.prefix)
            runs = set()
            for blob in blobs:
                parts = blob.name.split("/")
                if len(parts) > 1:
                    runs.add(parts[1])
            return sorted(runs)
        except ImportError:
            logger.error("google-cloud-storage not installed")
            return []
        except Exception as e:
            logger.error("GCS list failed: %s", e)
            return []
