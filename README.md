# 🔎 recon-toolkit

> Lightweight recon automation for CTF and authorised penetration testing. Wraps nmap, gobuster, whois, and dig into a single structured workflow with clean terminal output and optional JSON/Markdown reporting.

---

## ⚠️ Disclaimer

**This tool is for use on systems you own or have explicit written permission to test.** Unauthorised scanning is illegal. Use responsibly.

---

## Features

- 🔍 **Port scanning** via nmap (fast or full `-p-` mode)
- 📁 **Directory bruteforce** via gobuster
- 🌐 **DNS enumeration** (A, AAAA, MX, NS, TXT, CNAME)
- 📋 **WHOIS lookup**
- 📊 **Clean coloured terminal output**
- 💾 Optional **JSON export** and **Markdown report generation**

---

## Installation

```bash
git clone https://github.com/yeelaiii/recon-toolkit
cd recon-toolkit
```

**Requirements:** Python 3.8+ and the following tools installed:

```bash
# Debian/Ubuntu
sudo apt install nmap gobuster whois dnsutils
```

No Python dependencies beyond stdlib.

---

## Usage

```bash
# Full recon on a target
python3 recon_toolkit.py 10.10.10.1

# Fast mode (top ports only) + generate markdown report
python3 recon_toolkit.py 10.10.10.1 --fast --markdown

# Custom wordlist + save JSON
python3 recon_toolkit.py 10.10.10.1 --wordlist /usr/share/seclists/Discovery/Web-Content/common.txt --json

# Skip gobuster and whois (just nmap + DNS)
python3 recon_toolkit.py example.com --skip-gobuster --skip-whois
```

### Options

| Flag | Description |
|------|-------------|
| `--fast` | Fast nmap scan (top ports, `-T4 --open`) |
| `--wordlist PATH` | Custom wordlist for gobuster |
| `--skip-gobuster` | Skip directory bruteforce |
| `--skip-whois` | Skip WHOIS lookup |
| `--output-dir DIR` | Output directory (default: `recon_output/`) |
| `--json` | Save raw results as JSON |
| `--markdown` | Generate Markdown recon report |

---

## Sample Output

```
────────────────────────────────────────────────────────
  recon-toolkit · github.com/yeelaiii
────────────────────────────────────────────────────────
  Target : 10.10.10.1
  Time   : 2026-01-15 14:32:11
────────────────────────────────────────────────────────

  ⚠️  Only use on systems you own or have written permission to test.

  [*] Running nmap on 10.10.10.1 ...
  [+] nmap complete.
  [*] Running DNS enumeration on 10.10.10.1 ...
  [+] DNS enum complete. Found records: ['A']
  [*] Running whois on 10.10.10.1 ...
  [+] whois complete.
  [*] Running gobuster dir on http://10.10.10.1 ...
  [+] gobuster complete.

────────────────────────────────────────────────────────
  Recon complete.
────────────────────────────────────────────────────────
```

---

## Roadmap

- [ ] Subdomain enumeration mode
- [ ] HTTP header / tech stack fingerprinting
- [ ] Auto-screenshot of discovered web services
- [ ] Integration with Nmap NSE scripts
- [ ] HTML report export

---

## Author

**Elijah Soon** · [yeelaiii.github.io](https://yeelaiii.github.io) · SUTD CS&D · CCNA · OSCP (prep)
