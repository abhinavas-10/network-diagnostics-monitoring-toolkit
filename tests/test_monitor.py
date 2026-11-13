from network_toolkit.monitor import monitor_hosts

def test_monitor_records_initial_state(monkeypatch):
    import network_toolkit.monitor as monitor
    monkeypatch.setattr(monitor, "ping_host", lambda *a, **k: {
        "success": True, "packet_loss_percent": 0, "avg_latency_ms": 1.2, "error": None
    })
    records = monitor_hosts(["localhost"], interval=1, iterations=1)
    assert len(records) == 1
    assert records[0]["status_change"] == "INITIAL_UP"
