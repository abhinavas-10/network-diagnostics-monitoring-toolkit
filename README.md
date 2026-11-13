# Network Diagnostics and Monitoring Toolkit

A cross-platform Python command-line application for basic network troubleshooting and host availability monitoring. It demonstrates practical networking concepts including ICMP ping, DNS resolution, traceroute, TCP connectivity, periodic monitoring, structured logging, and CSV/JSON reporting.

## Features

- Ping monitoring: availability, packet loss, and average latency where reported by the OS.
- DNS lookup: canonical hostname, aliases, and IPv4 addresses.
- Traceroute: uses `tracert` on Windows and `traceroute` on Linux/macOS.
- TCP port checker: tests whether a TCP connection can be established.
- Network/system information: hostname, locally resolved IP, OS and Python version.
- Periodic host monitoring with UP/DOWN transition records.
- Timestamped application logs in `logs/network_toolkit.log`.
- JSON and CSV report export.
- Automated tests using pytest.

## Requirements

- Python 3.9+
- Windows 11, Linux, or macOS
- Git (for version control)
- `ping` is normally included with the OS. On Linux, install `traceroute` if it is not present.

## Setup (Windows PowerShell)

```powershell
git clone https://github.com/YOUR_USERNAME/network-diagnostics-monitoring-toolkit.git
cd network-diagnostics-monitoring-toolkit
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

If PowerShell blocks activation, run this for the current terminal only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Commands

```powershell
netdiag info
netdiag ping 8.8.8.8
netdiag ping example.com --count 5 --timeout 2
netdiag dns google.com
netdiag trace 8.8.8.8
netdiag port google.com 443
netdiag port example.com 22 --timeout 2
netdiag monitor --config config/hosts.json --iterations 3
```

If the `netdiag` command is not recognized, use:

```powershell
python -m network_toolkit.cli info
python -m network_toolkit.cli ping 8.8.8.8
```

Monitoring runs until Ctrl+C if `--iterations` is omitted. Reports are saved as `reports/monitor.csv` and `reports/monitor.json`.

## Linux setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Install traceroute if required (for example, `sudo apt install traceroute` on Debian/Ubuntu).

## Tests

```powershell
python -m pytest -v
```

Tests use localhost and a temporary local TCP server. They do not require access to external websites.

## Example monitoring configuration

Edit `config/hosts.json`:

```json
{
  "hosts": ["8.8.8.8", "1.1.1.1", "example.com"],
  "interval_seconds": 30,
  "timeout_seconds": 2
}
```

## Output and logs

- `logs/network_toolkit.log`: application events and errors.
- `reports/monitor.json`: detailed monitoring records.
- `reports/monitor.csv`: tabular monitoring records.

The ping and traceroute implementations rely on operating-system utilities and their output formats. Some networks block ICMP or traceroute probes; a failed ping does not necessarily mean a TCP service is unavailable. Use the TCP port checker to test a specific service port.

## Troubleshooting notes

- **Ping fails:** ICMP may be blocked by a firewall or network policy.
- **DNS fails:** verify the hostname and DNS connectivity; try another resolver/network.
- **TCP port fails:** the service may be stopped, filtered, or listening on a different port.
- **Traceroute unavailable:** install the platform's traceroute utility; Windows uses `tracert`.
- **Permission/network restrictions:** run only diagnostics you are authorized to perform.

## Project structure

```text
network-diagnostics-monitoring-toolkit/
├── config/
│   └── hosts.json
├── network_toolkit/
│   ├── __init__.py
│   ├── cli.py
│   ├── diagnostics.py
│   ├── monitor.py
│   ├── reporting.py
│   └── utils.py
├── tests/
│   ├── test_diagnostics.py
│   ├── test_monitor.py
│   └── test_reporting.py
├── .gitignore
├── pyproject.toml
└── README.md
```

## Resume description

**Network Diagnostics and Monitoring Toolkit | Python, TCP/IP, DNS, Subprocess, Socket, Pytest**

- Developed a cross-platform Python CLI tool to diagnose network connectivity using ICMP ping, DNS resolution, traceroute, and TCP port checks.
- Implemented periodic host monitoring with availability transition detection, timestamped logging, and CSV/JSON report generation.
- Added input validation, timeout handling, OS-aware command execution, and automated pytest coverage.

Only list features and tests that you have personally run and verified.

## Suggested future enhancements

- IPv6 DNS and connectivity support.
- Interface enumeration and default gateway detection.
- Configurable alert thresholds and retry policies.
- Historical uptime and packet-loss summaries.
- Rich terminal tables and color-coded output.
