import socket
from network_toolkit.diagnostics import dns_lookup, check_tcp_port, network_info

def test_dns_lookup_localhost():
    result = dns_lookup("localhost")
    assert result["success"] is True
    assert result["ip_addresses"]

def test_dns_lookup_invalid_domain():
    result = dns_lookup("this-domain-should-not-exist.invalid")
    assert result["success"] is False
    assert result["error"]

def test_tcp_port_open():
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]
    try:
        result = check_tcp_port("127.0.0.1", port)
        assert result["success"] is True
        assert result["port"] == port
    finally:
        server.close()

def test_tcp_port_invalid():
    import pytest
    with pytest.raises(ValueError):
        check_tcp_port("localhost", 70000)

def test_network_info_has_required_fields():
    result = network_info()
    assert result["hostname"]
    assert "local_ip" in result
    assert result["system"]
