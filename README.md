<div align="center">
  <h1>â˜ CloudSentry</h1>
  <p><strong>Automated Multicloud Failover â€” Azure Primary / AWS Secondary / Cloudflare DNS</strong></p>

  ![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
  ![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
  ![Azure](https://img.shields.io/badge/Azure-Sweden_Central-0078D4?style=flat-square&logo=microsoftazure&logoColor=white)
  ![AWS](https://img.shields.io/badge/AWS-eu--west--1-FF9900?style=flat-square&logo=amazonaws&logoColor=white)
  ![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
</div>

---

## What Is CloudSentry?

CloudSentry is a production-grade automated multicloud failover system that monitors a primary cloud deployment, detects failures in real time, and executes DNS-based traffic switching to a secondary provider without human intervention.

Built with Python, Docker, Nginx, Flask, and the Cloudflare API. No proprietary vendor tooling. No enterprise licences required.

## Key Results

Empirically validated across 30 controlled trials:

| Policy | Detection Latency | vs Manual (~240s) |
|--------|------------------|------------------|
| Aggressive (5s Â· Ã—2) | **10.4s** | 95.6% faster |
| Balanced (15s Â· Ã—3)  | **42.3s** | 82.4% faster |
| Conservative (30s Â· Ã—5) | **163.7s** | 31.8% faster |

30/30 trials resulted in successful automated failover. StdDev < 2s across all conditions.

## Architecture

```
Client â†’ Cloudflare DNS â†’ Azure Primary (active)
                       â†˜ AWS Secondary  (standby)
                       â†‘
              Python Failover Controller
              (health checks + Cloudflare API)
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Application | Python + Flask + Gunicorn |
| Reverse Proxy | Nginx |
| Containerisation | Docker + Docker Compose |
| Primary Cloud | Azure Standard_B2ats_v2 (Sweden Central) |
| Secondary Cloud | AWS t3.micro (eu-west-1) |
| DNS & Failover | Cloudflare API |
| Dashboard | CloudSentry real-time monitoring UI |

## Quick Start

```bash
git clone https://github.com/DouglasAmesinu/cloudsentry-multicloud-failover.git
cd cloudsentry-multicloud-failover
cp controller/config.py.example controller/config.py
# Fill in your credentials
pip install flask flask-cors requests
cd controller && python api_server.py
# Open dashboard/cloudsentry_dashboard.html in Chrome
```

See [docs/setup-guide.md](docs/setup-guide.md) for full instructions.

## Project Structure

```
cloudsentry-multicloud-failover/
â”œâ”€â”€ app/                    # Flask app + Docker
â”œâ”€â”€ controller/             # Failover controller + API
â”œâ”€â”€ dashboard/              # CloudSentry monitoring UI
â”œâ”€â”€ results/                # Experimental trial data
â””â”€â”€ docs/                   # Setup and results docs
```

## License

MIT â€” see [LICENSE](LICENSE)

---
<div align="center"><sub>Built with Python Â· Docker Â· Azure Â· AWS Â· Cloudflare</sub></div>
