#!/usr/bin/env python3
"""
recon-toolkit
=============
Lightweight recon automation for CTF and authorised penetration testing.
Wraps nmap, gobuster/ffuf, and whois into a single structured workflow
with clean output and optional JSON/Markdown reporting.

Author: Elijah Soon (github.com/yeelaiii)

⚠️  For use on systems you own or have explicit written permission to test.
"""

import argparse
import subprocess
import json
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def info(msg):  print(f"  {CYAN}[*]{RESET} {msg}")
def ok(msg):    print(f"  {GREEN}[+]{RESET} {msg}")
def warn(msg):  print(f"  {YELLOW}[!]{RESET} {msg}")
def err(msg):   print(f"  {RED}[-]{RESET} {msg}", file=sys.stderr)

def check_tool(name: str) -> bool:
    if shutil.which(name):
        return True
    warn(f"'{name}' not found in PATH — skipping dependent steps.")
    return False

def run(cmd: list, timeout: int = 300) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        warn(f"Command timed out after {timeout}s: {' '.join(cmd)}")
        return -1, "", "timeout"
    except FileNotFoundError:
        return -1, "", f"tool not found: {cmd[0]}"


# ─────────────────────────────────────────────────────────────
# Recon modules
# ─────────────────────────────────────────────────────────────

def run_nmap(target: str, fast: bool = False) -> dict:
    info(f"Running nmap on {target} ...")
    flags = ["-T4", "--open"] if fast else ["-sV", "-sC", "-T4", "--open", "-p-"]
    rc, stdout, stderr = run(["nmap"] + flags + [target], timeout=600)

    result = {"command": f"nmap {' '.join(flags)} {target}", "output": stdout, "error": stderr}

    if rc == 0:
        ok("nmap complete.")
    else:
        warn(f"nmap exited with code {rc}")

    return result


def run_gobuster(target: str, wordlist: str) -> dict:
    if not check_tool("gobuster"):
        return {"skipped": True, "reason": "gobuster not installed"}

    if not os.path.isfile(wordlist):
        warn(f"Wordlist not found: {wordlist}")
        return {"skipped": True, "reason": f"wordlist not found: {wordlist}"}

    # Ensure target has scheme
    url = target if target.startswith("http") else f"http://{target}"
    info(f"Running gobuster dir on {url} ...")

    rc, stdout, stderr = run([
        "gobuster", "dir",
        "-u", url,
        "-w", wordlist,
        "-t", "50",
        "--no-error",
        "-q"
    ], timeout=300)

    ok("gobuster complete.") if rc == 0 else warn(f"gobuster exited {rc}")
    return {"command": f"gobuster dir -u {url} -w {wordlist}", "output": stdout, "error": stderr}


def run_whois(target: str) -> dict:
    if not check_tool("whois"):
        return {"skipped": True, "reason": "whois not installed"}

    info(f"Running whois on {target} ...")
    rc, stdout, stderr = run(["whois", target], timeout=30)
    ok("whois complete.") if rc == 0 else warn(f"whois exited {rc}")
    return {"output": stdout, "error": stderr}


def run_dns_enum(target: str) -> dict:
    """Basic DNS enumeration using dig."""
    if not check_tool("dig"):
        return {"skipped": True, "reason": "dig not installed"}

    info(f"Running DNS enumeration on {target} ...")
    records = {}
    for rtype in ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]:
        rc, stdout, _ = run(["dig", "+short", rtype, target], timeout=15)
        if rc == 0 and stdout.strip():
            records[rtype] = stdout.strip().splitlines()

    ok(f"DNS enum complete. Found records: {list(records.keys())}")
    return {"records": records}


# ─────────────────────────────────────────────────────────────
# Report generation
# ─────────────────────────────────────────────────────────────

def generate_markdown(target: str, results: dict, outfile: str):
    lines = [
        f"# Recon Report: `{target}`",
        f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Tool:** recon-toolkit (github.com/yeelaiii)\n",
        "---\n",
    ]

    if "nmap" in results:
        lines += ["## Port Scan (nmap)\n", f"```\n{results['nmap'].get('output','')}\n```\n"]

    if "dns" in results and "records" in results["dns"]:
        lines += ["## DNS Records\n"]
        for rtype, vals in results["dns"]["records"].items():
            lines.append(f"**{rtype}**: {', '.join(vals)}\n")
        lines.append("\n")

    if "whois" in results:
        lines += ["## WHOIS\n", f"```\n{results['whois'].get('output','')[:2000]}\n```\n"]

    if "gobuster" in results and not results["gobuster"].get("skipped"):
        lines += ["## Directory Bruteforce (gobuster)\n", f"```\n{results['gobuster'].get('output','')}\n```\n"]

    lines += ["\n---\n", "*⚠️ Only use on systems you own or have explicit permission to test.*"]

    with open(outfile, "w") as f:
        f.write("\n".join(lines))
    ok(f"Markdown report saved: {outfile}")


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="recon-toolkit — lightweight recon automation for authorised pentesting & CTFs"
    )
    parser.add_argument("target", help="Target IP or domain")
    parser.add_argument("--fast", action="store_true", help="Fast nmap scan (top ports only)")
    parser.add_argument("--wordlist", default="/usr/share/wordlists/dirb/common.txt",
                        help="Wordlist for gobuster (default: dirb/common.txt)")
    parser.add_argument("--skip-gobuster", action="store_true", help="Skip directory bruteforce")
    parser.add_argument("--skip-whois", action="store_true", help="Skip WHOIS lookup")
    parser.add_argument("--output-dir", default="recon_output", help="Output directory")
    parser.add_argument("--json", action="store_true", help="Save raw results as JSON")
    parser.add_argument("--markdown", action="store_true", help="Generate Markdown report")
    args = parser.parse_args()

    print(f"\n{BOLD}{'─'*56}{RESET}")
    print(f"{BOLD}  recon-toolkit · github.com/yeelaiii{RESET}")
    print(f"{'─'*56}")
    print(f"  Target : {args.target}")
    print(f"  Time   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'─'*56}\n")
    print(f"  {RED}⚠️  Only use on systems you own or have written permission to test.{RESET}\n")

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    results = {}

    if check_tool("nmap"):
        results["nmap"] = run_nmap(args.target, fast=args.fast)

    results["dns"] = run_dns_enum(args.target)

    if not args.skip_whois:
        results["whois"] = run_whois(args.target)

    if not args.skip_gobuster:
        results["gobuster"] = run_gobuster(args.target, args.wordlist)

    print(f"\n{BOLD}{'─'*56}{RESET}")
    print(f"{BOLD}  Recon complete.{RESET}")
    print(f"{'─'*56}\n")

    if args.json:
        json_path = os.path.join(args.output_dir, f"{args.target.replace('.','_')}_recon.json")
        with open(json_path, "w") as f:
            json.dump(results, f, indent=2)
        ok(f"JSON saved: {json_path}")

    if args.markdown:
        md_path = os.path.join(args.output_dir, f"{args.target.replace('.','_')}_report.md")
        generate_markdown(args.target, results, md_path)


if __name__ == "__main__":
    main()
