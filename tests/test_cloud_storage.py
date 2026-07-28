import tempfile
from pathlib import Path

from gli_flow.cloud.storage import CloudStorageConfig, CloudStorageManager, CloudProvider


def test_cloud_storage_config_defaults():
    c = CloudStorageConfig()
    assert c.provider == CloudProvider.S3
    assert c.bucket == "gli-flow-runs"
    assert c.prefix == "runs"
    assert c.region == "us-east-1"


def test_cloud_storage_config_gcs():
    c = CloudStorageConfig(provider=CloudProvider.GCS, bucket="my-bucket")
    assert c.provider == CloudProvider.GCS
    assert c.bucket == "my-bucket"


def test_cloud_storage_manager_init():
    c = CloudStorageConfig()
    m = CloudStorageManager(c)
    assert m.config.provider == CloudProvider.S3


def test_cloud_storage_list_runs_s3_no_creds():
    c = CloudStorageConfig(provider=CloudProvider.S3, bucket="nonexistent-bucket-for-testing-12345")
    m = CloudStorageManager(c)
    runs = m.list_runs()
    assert runs == []


def test_cloud_storage_upload_no_boto3():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "test.txt").write_text("hello")
        c = CloudStorageConfig(provider=CloudProvider.S3, bucket="test-bucket")
        m = CloudStorageManager(c)
        url = m.upload_run(tmp, "test_run_123")
        assert url == ""
