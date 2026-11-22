"""Lab-only scanner interface; scan target is fixed at server startup."""
import ipaddress
import os
import re
import subprocess
from flask import Flask, jsonify, render_template

app = Flask(__name__)

TARGET = os.environ.get("LAB_TARGET", "").strip()


def validated_target(value: str) -> str:
    """Require an explicitly configured, private IPv4 lab address."""
    if not value:
        raise ValueError("Set LAB_TARGET to your instructor-approved private IPv4 lab host.")
    try:
        address = ipaddress.ip_address(value)
    except ValueError as exc:
        raise ValueError("LAB_TARGET must be a numeric IPv4 address, not a hostname.") from exc
    if address.version != 4 or not address.is_private or address.is_link_local or address.is_multicast or address.is_unspecified:
        raise ValueError("LAB_TARGET must be an approved private IPv4 lab address.")
    return str(address)


@app.get("/")
def home():
    try:
        target = validated_target(TARGET)
        warning = None
    except ValueError as exc:
        target = "Not configured"
        warning = str(exc)
    return render_template("index.html", target=target, warning=warning)


@app.post("/scan")
def scan():
    try:
        target = validated_target(TARGET)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    # No user-supplied target, no shell, and no intrusive Nmap options.
    command = ["nmap", "-sT", "-Pn", "-n", "-p", "20,21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5000", "-sV", "--version-light", "--open", "-oG", "-", target]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=75, check=False)
    except FileNotFoundError:
        return jsonify(error="Nmap is not installed. Install it and restart the app."), 500
    except subprocess.TimeoutExpired:
        return jsonify(error="Scan timed out after 75 seconds."), 504

    if result.returncode != 0:
        return jsonify(error=(result.stderr.strip() or "Nmap scan failed")[:600]), 500

    ports = []
    for line in result.stdout.splitlines():
        if not line.startswith("Host:") or "Ports:" not in line:
            continue
        # Grepable Nmap output: port/state/protocol/owner/service/sunrpc/version/
        entry_text = line.split("Ports:", 1)[1].split("Ignored State:", 1)[0].strip()
        for item in re.split(r",\s*(?=\d+/)", entry_text):
            fields = item.strip().split("/")
            if len(fields) >= 5 and fields[1] == "open":
                ports.append({
                    "port": int(fields[0]),
                    "protocol": fields[2],
                    "service": fields[4] or "unknown",
                    "version": fields[6].strip() if len(fields) > 6 else "",
                })
    ports.sort(key=lambda p: p["port"])
    return jsonify(target=target, ports=ports, count=len(ports), note="Only the top 20 common TCP ports were checked. No result does not mean no ports are open.")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
