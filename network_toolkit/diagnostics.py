"""Cross-platform network diagnostic operations."""
import platform
import re
import socket
import subprocess
import time
from typing import Any, Dict, List, Optional
from .utils import timestamp

def ping_host(host: str, count: int = 4, timeout: int = 2) -> Dict[str, Any]:
    if not host or count < 1 or timeout < 1:
        raise ValueError("host, count and timeout must be valid")
    system = platform.system().lower()
    if system == "windows":
        command = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
    else:
        command = ["ping", "-c", str(count), "-W", str(timeout), host]
    started = time.perf_counter()
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                timeout=count * timeout + 5, check=False)
        output = (result.stdout or "") + (result.stderr or "")
        received = 0
        loss = 100.0
        latency: Optional[float] = None

        # Windows: "Received = 4"; Linux/macOS: "4 received"
        match = re.search(r"Received\s*=\s*(\d+)", output, re.I)
        if not match:
            match = re.search(r"(\d+)\s+received", output, re.I)
        if match:
            received = int(match.group(1))
        sent_match = re.search(r"Sent\s*=\s*(\d+)", output, re.I)
        sent = int(sent_match.group(1)) if sent_match else count
        loss_match = re.search(r"(\d+(?:\.\d+)?)%\s*packet loss", output, re.I)
        if loss_match:
            loss = float(loss_match.group(1))
        else:
            loss = max(0.0, 100.0 * (sent - received) / sent) if sent else 100.0

        # Average time from Windows, Linux and macOS output.
        avg = re.search(r"(?:Average\s*=\s*|avg(?:\s*/\s*\w+)*\s*=\s*)"
                        r"([\d.]+)\s*ms", output, re.I)
        if avg:
            latency = float(avg.group(1))
        else:
            times = [float(x) for x in re.findall(r"time[=<]([\d.]+)\s*ms", output, re.I)]
            if times:
                latency = sum(times) / len(times)

        return {
            "timestamp": timestamp(), "operation": "ping", "target": host,
            "success": received > 0, "sent": sent, "received": received,
            "packet_loss_percent": round(loss, 2), "avg_latency_ms": latency,
            "return_code": result.returncode, "error": None if received else output.strip()[-500:]
        }
    except FileNotFoundError:
        return _failure("ping", host, "Ping executable not found")
    except subprocess.TimeoutExpired:
        return _failure("ping", host, "Ping command timed out")
    except OSError as exc:
        return _failure("ping", host, str(exc))

def dns_lookup(host: str) -> Dict[str, Any]:
    if not host:
        raise ValueError("hostname cannot be empty")
    try:
        canonical, aliases, addresses = socket.gethostbyname_ex(host)
        return {"timestamp": timestamp(), "operation": "dns", "target": host,
                "success": True, "canonical_name": canonical,
                "aliases": aliases, "ip_addresses": sorted(set(addresses)), "error": None}
    except (socket.gaierror, OSError) as exc:
        return {"timestamp": timestamp(), "operation": "dns", "target": host,
                "success": False, "canonical_name": None, "aliases": [],
                "ip_addresses": [], "error": str(exc)}

def traceroute(host: str, max_hops: int = 15, timeout: int = 2) -> Dict[str, Any]:
    if not host or max_hops < 1 or timeout < 1:
        raise ValueError("host, max_hops and timeout must be valid")
    system = platform.system().lower()
    if system == "windows":
        command = ["tracert", "-d", "-h", str(max_hops), "-w", str(timeout * 1000), host]
    else:
        command = ["traceroute", "-n", "-m", str(max_hops), "-w", str(timeout), host]
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                timeout=max_hops * timeout * 3 + 10, check=False)
        output = (result.stdout or "") + (result.stderr or "")
        return {"timestamp": timestamp(), "operation": "traceroute", "target": host,
                "success": result.returncode == 0, "return_code": result.returncode,
                "output": output.strip(), "error": None if result.returncode == 0 else output.strip()[-500:]}
    except FileNotFoundError:
        return _failure("traceroute", host, "Traceroute executable not found; install traceroute on Linux")
    except subprocess.TimeoutExpired:
        return _failure("traceroute", host, "Traceroute command timed out")
    except OSError as exc:
        return _failure("traceroute", host, str(exc))

def check_tcp_port(host: str, port: int, timeout: float = 3.0) -> Dict[str, Any]:
    if not host or not 1 <= int(port) <= 65535:
        raise ValueError("Provide a hostname and TCP port between 1 and 65535")
    started = time.perf_counter()
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            elapsed = (time.perf_counter() - started) * 1000
            return {"timestamp": timestamp(), "operation": "tcp_port", "target": host,
                    "port": int(port), "success": True,
                    "response_time_ms": round(elapsed, 2), "error": None}
    except (socket.timeout, TimeoutError) as exc:
        return {"timestamp": timestamp(), "operation": "tcp_port", "target": host,
                "port": int(port), "success": False, "response_time_ms": None,
                "error": str(exc) or "Connection timed out"}
    except OSError as exc:
        return {"timestamp": timestamp(), "operation": "tcp_port", "target": host,
                "port": int(port), "success": False, "response_time_ms": None, "error": str(exc)}

def network_info() -> Dict[str, Any]:
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except OSError:
        local_ip = "Unavailable"
    return {"timestamp": timestamp(), "hostname": hostname, "local_ip": local_ip,
            "platform": platform.platform(), "system": platform.system(),
            "release": platform.release(), "python_version": platform.python_version()}

def _failure(operation: str, host: str, message: str) -> Dict[str, Any]:
    return {"timestamp": timestamp(), "operation": operation, "target": host,
            "success": False, "error": message}
