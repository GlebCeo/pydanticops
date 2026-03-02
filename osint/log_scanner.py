import os, re
from dataclasses import dataclass
from collections import defaultdict
from pathlib import Path

@dataclass
class SuspiciousEntry:
    ip: str
    count: int
    pattern: str

MALICIOUS_UA = re.compile(r"(sqlmap|nikto|masscan|zgrab|nmap|curl/|wget/)", re.IGNORECASE)
NGINX_RE = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[.+?\] "\S+ \S+ \S+" (?P<status>\d+) \d+ ".*?" "(?P<ua>[^"]*)"'
)

class LogScanner:
    def _default_log(self):
        for p in [Path("/var/log/nginx/access.log"), Path("/var/log/sglang/requests.log")]:
            if p.exists(): return p
        return None

    def scan(self, log_path=None, threshold_rpm=100) -> list[SuspiciousEntry]:
        path = Path(log_path) if log_path else self._default_log()
        if not path or not path.exists(): return []
        counts, patterns = defaultdict(int), defaultdict(set)
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    m = NGINX_RE.match(line)
                    if not m: continue
                    ip, status, ua = m.group("ip"), int(m.group("status")), m.group("ua")
                    counts[ip] += 1
                    if status in (400,401,403,404,429): patterns[ip].add(f"HTTP{status}")
                    if MALICIOUS_UA.search(ua): patterns[ip].add("MaliciousUA")
        except PermissionError:
            return []
        results = [
            SuspiciousEntry(ip=ip, count=c, pattern=", ".join(patterns.get(ip,{"HighVolume"})))
            for ip, c in counts.items() if c >= threshold_rpm or patterns.get(ip)
        ]
        return sorted(results, key=lambda e: e.count, reverse=True)[:20]
