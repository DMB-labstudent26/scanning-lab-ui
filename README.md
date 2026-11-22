# Lab TCP Scanner — Vibe Coding 2

A small, AI-assisted Flask web interface that runs a **light TCP scan against one instructor-approved lab IP** and displays open ports, services, and detected versions.

> **Lab targets only.** Use solely on systems that your instructor explicitly authorizes. Do not scan public or unrelated hosts.

## Requirements

- Python 3.9 or later
- Nmap installed and available on your PATH
- Access to your assigned lab target (including any required lab VM/network)

## Run on macOS / Linux

```bash
cd scanning-lab-ui
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export LAB_TARGET="YOUR_APPROVED_PRIVATE_LAB_IP"
python app.py
```

Replace `YOUR_APPROVED_PRIVATE_LAB_IP` with the **exact private IPv4 address assigned by your instructor** (example format: `10.x.x.x`). Do not leave the placeholder. Install Nmap on macOS using its official installer or Homebrew (`brew install nmap`).

Open **http://127.0.0.1:5000** in your browser, click **Run light TCP scan**, and inspect the table.

## What it runs

```text
nmap -sT -Pn -n --top-ports 20 -sV --version-light --open -oG - <approved-ip>
```

- `-sT`: TCP connect scan; no raw packet privilege required.
- `-Pn`: use the known lab address without a preliminary host discovery stage.
- `-n`: skip DNS lookups.
- `--top-ports 20`: check only 20 common ports.
- `-sV --version-light`: limited service detection (may contact open services).
- `--open`: display open ports.
- `-oG -`: produce parseable scan output for the table.

The target is **fixed by the `LAB_TARGET` environment variable**, not editable in the browser. The backend validates that it is a private IPv4 address, but **private does not automatically mean authorized**: verify instructor approval before running. The app binds to localhost only; it cannot be used to scan arbitrary addresses from the UI. Scans time out after 75 seconds.

## Screenshot for submission

With the approved lab host reachable, run the app, click **Run light TCP scan**, and capture one screenshot showing the browser URL, fixed target, the completion status, and results table. On Mac, use **Command + Shift + 4**. Do not fabricate scan results; if the scan fails, fix connectivity or ask the instructor for the correct lab address.

## GitHub submission

Create a repository named `scanning-lab-ui`, upload the files from this directory, and submit its repo URL in the form `https://github.com/YOUR_USERNAME/scanning-lab-ui`. The screenshot is also required by the assignment; add your **real** screenshot to the repo once captured.
