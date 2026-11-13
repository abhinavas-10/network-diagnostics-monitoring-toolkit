"""Periodic host monitoring with availability-change events."""
import time
from typing import Any, Dict, List, Optional
from .diagnostics import ping_host
from .utils import timestamp

def monitor_hosts(hosts: List[str], interval: int = 30, timeout: int = 2,
                  iterations: Optional[int] = None, logger=None) -> List[Dict[str, Any]]:
    if not hosts:
        raise ValueError("At least one host is required")
    if interval < 1:
        raise ValueError("interval must be at least one second")
    records: List[Dict[str, Any]] = []
    previous: Dict[str, bool] = {}
    cycle = 0
    try:
        while iterations is None or cycle < iterations:
            for host in hosts:
                result = ping_host(host, count=1, timeout=timeout)
                status = bool(result.get("success"))
                record = {"timestamp": timestamp(), "operation": "monitor",
                          "target": host, "success": status,
                          "packet_loss_percent": result.get("packet_loss_percent"),
                          "avg_latency_ms": result.get("avg_latency_ms"),
                          "status_change": None, "error": result.get("error")}
                if host in previous and previous[host] != status:
                    record["status_change"] = "UP" if status else "DOWN"
                    if logger:
                        logger.warning("%s changed to %s", host, record["status_change"])
                elif host not in previous:
                    record["status_change"] = "INITIAL_UP" if status else "INITIAL_DOWN"
                previous[host] = status
                records.append(record)
                if logger:
                    logger.info("Monitor %s: %s", host, "UP" if status else "DOWN")
            cycle += 1
            if iterations is None or cycle < iterations:
                time.sleep(interval)
    except KeyboardInterrupt:
        if logger:
            logger.info("Monitoring stopped by user")
    return records
