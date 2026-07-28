from gli_flow.scheduler.remote import RemoteWorkerConfig, RemoteWorkerResult, RemoteWorker


def test_remote_worker_config_defaults():
    c = RemoteWorkerConfig(host="remote.example.com")
    assert c.host == "remote.example.com"
    assert c.port == 22
    assert c.ssh_host == "remote.example.com"


def test_remote_worker_config_with_user():
    c = RemoteWorkerConfig(host="10.0.0.1", port=2222, user="flowuser", key_path="/home/me/.ssh/id_rsa")
    assert c.port == 2222
    assert c.ssh_host == "flowuser@10.0.0.1"
    assert c.key_path == "/home/me/.ssh/id_rsa"


def test_remote_worker_result_dataclass():
    r = RemoteWorkerResult(success=True, run_id="run_123_test", design_name="test", duration=42.5, returncode=0)
    assert r.success
    assert r.run_id == "run_123_test"
    assert r.duration == 42.5


def test_remote_worker_build_ssh_cmd_default():
    c = RemoteWorkerConfig(host="example.com")
    w = RemoteWorker("test", c)
    cmd = w._build_ssh_cmd("echo ok")
    assert "ssh" in cmd
    assert "example.com" in cmd
    assert "echo ok" in cmd[-1]


def test_remote_worker_build_ssh_cmd_with_key():
    c = RemoteWorkerConfig(host="10.0.0.1", port=2222, user="u", key_path="/key.pem")
    w = RemoteWorker("test", c)
    cmd = w._build_ssh_cmd("gli-flow run /tmp/design")
    assert "-p" in cmd
    assert "2222" in cmd
    assert "-i" in cmd
    assert "/key.pem" in cmd
    assert "u@10.0.0.1" in cmd


def test_remote_worker_check_connection_fails_without_ssh():
    c = RemoteWorkerConfig(host="nonexistent.invalid")
    w = RemoteWorker("test", c)
    result = w.check_connection()
    assert result is False
