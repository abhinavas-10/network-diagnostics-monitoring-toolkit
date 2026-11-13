"""Command-line interface."""
import argparse
import json
from pathlib import Path
from .diagnostics import ping_host, dns_lookup, traceroute, check_tcp_port, network_info
from .monitor import monitor_hosts
from .reporting import export_csv, export_json
from .utils import setup_logging

def _print(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

def build_parser():
    parser = argparse.ArgumentParser(
        prog="netdiag",
        description="Network Diagnostics and Monitoring Toolkit"
    )
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("ping", help="Check host availability and latency")
    p.add_argument("host")
    p.add_argument("-c", "--count", type=int, default=4)
    p.add_argument("-t", "--timeout", type=int, default=2)

    p = sub.add_parser("dns", help="Resolve a hostname")
    p.add_argument("host")

    p = sub.add_parser("trace", help="Trace the route to a host")
    p.add_argument("host")
    p.add_argument("--max-hops", type=int, default=15)
    p.add_argument("--timeout", type=int, default=2)

    p = sub.add_parser("port", help="Check TCP port reachability")
    p.add_argument("host")
    p.add_argument("port", type=int)
    p.add_argument("--timeout", type=float, default=3.0)

    sub.add_parser("info", help="Show local network and system information")

    p = sub.add_parser("monitor", help="Monitor hosts from a JSON config")
    p.add_argument("--config", default="config/hosts.json")
    p.add_argument("--iterations", type=int, default=None,
                   help="Number of monitoring cycles; omit to run until Ctrl+C")
    p.add_argument("--output", default="reports/monitor")
    return parser

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    logger = setup_logging(level=args.log_level)
    try:
        if args.command == "ping":
            result = ping_host(args.host, args.count, args.timeout)
            logger.info("Ping completed for %s", args.host)
            _print(result)
            return 0 if result["success"] else 1
        if args.command == "dns":
            result = dns_lookup(args.host)
            _print(result)
            return 0 if result["success"] else 1
        if args.command == "trace":
            result = traceroute(args.host, args.max_hops, args.timeout)
            _print(result)
            return 0 if result["success"] else 1
        if args.command == "port":
            result = check_tcp_port(args.host, args.port, args.timeout)
            _print(result)
            return 0 if result["success"] else 1
        if args.command == "info":
            _print(network_info())
            return 0
        if args.command == "monitor":
            config_path = Path(args.config)
            with config_path.open(encoding="utf-8") as handle:
                config = json.load(handle)
            hosts = config.get("hosts", [])
            records = monitor_hosts(hosts, int(config.get("interval_seconds", 30)),
                                    int(config.get("timeout_seconds", 2)),
                                    args.iterations, logger)
            json_path = export_json(records, args.output + ".json")
            csv_path = export_csv(records, args.output + ".csv")
            print(f"Reports saved: {json_path} and {csv_path}")
            return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        logger.error("%s", exc)
        parser.exit(2, f"Error: {exc}\\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
