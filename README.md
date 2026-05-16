<div align="center">
  <h1>CloudSentry</h1>
  <p><strong>Automated Multicloud Failover — Azure Primary / AWS Secondary / Cloudflare DNS</strong></p>

  ![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
  ![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
  ![Azure](https://img.shields.io/badge/Azure-Sweden_Central-0078D4?style=flat-square&logo=microsoftazure&logoColor=white)
  ![AWS](https://img.shields.io/badge/AWS-eu--west--1-FF9900?style=flat-square&logo=amazonaws&logoColor=white)
  ![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
</div>

---

## What Is CloudSentry?

CloudSentry is a production-grade automated multicloud failover system that monitors a primary cloud deployment, detects failures in real time, and executes DNS-based traffic switching to a secondary provider without human intervention.

Built with Python, Docker, Nginx, Flask, and the Cloudflare API. No proprietary vendor tooling. No enterprise licences required. Fully reproducible on any two cloud providers.

---

## How It Works

1. The **failover controller** runs health checks against both providers at a configurable interval
2. On detecting consecutive failures beyond a defined threshold, it calls the **Cloudflare API** to update the DNS A record
3. Client traffic automatically routes to the secondary provider within the TTL window
4. The **CloudSentry dashboard** shows all of this happening in real time

---

## Key Results

Empirically validated across 30 controlled trials:

| Policy | Mean Detection Latency | vs Manual Failover (~240s) |
|--------|----------------------|--------------------------|
| Aggressive (5s interval, 2 failures) | 10.4s | 95.6% faster |
| Balanced (15s interval, 3 failures)  | 42.3s | 82.4% faster |
| Conservative (30s interval, 5 failures) | 163.7s | 31.8% faster |

- 30 out of 30 trials resulted in successful automated failover
- Standard deviation below 2 seconds across all six conditions
- Application failures detected consistently faster than VM failures

---

## Architecture

```
Client Request
      |
      v
Cloudflare DNS  (douglasfailover.xyz, TTL 60s)
      |
      |-- Normal operation --> Azure Primary (Sweden Central)
      |
      |-- After failover  --> AWS Secondary (eu-west-1)

Failover Controller (runs independently)
      |
      |-- Health checks both providers every N seconds
      |-- On threshold breach: calls Cloudflare API
      |-- Updates DNS A record to secondary provider
```

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Application | Python + Flask + Gunicorn | Stateless web service |
| Reverse Proxy | Nginx | Health check endpoint, request routing |
| Containerisation | Docker + Docker Compose | Provider-agnostic deployment |
| Primary Cloud | Azure Standard_B2ats_v2 | Active traffic handler |
| Secondary Cloud | AWS t3.micro | Passive standby |
| DNS and Failover | Cloudflare API | Provider-independent traffic switching |
| Controller | Python 3 (custom) | Health monitoring and state machine |
| Dashboard | CloudSentry UI | Real-time monitoring interface |

---

## Health Check Configurations

| Config | Interval | Timeout | Threshold | Theoretical Min RTO |
|--------|----------|---------|-----------|-------------------|
| A — Aggressive   | 5s  | 3s  | 2 failures | 10s  |
| B — Balanced     | 15s | 5s  | 3 failures | 45s  |
| C — Conservative | 30s | 10s | 5 failures | 150s |

---

## State Machine

The controller operates across three states:

```
PRIMARY_HEALTHY  -->  FAILOVER_ACTIVE  -->  RECOVERING
```

- **PRIMARY_HEALTHY** — all traffic routes to Azure, health checks passing
- **FAILOVER_ACTIVE** — threshold breached, DNS switched to AWS
- **RECOVERING** — Azure restored, awaiting manual switchback

---

## Quick Start

```bash
git clone https://github.com/DouglasAmesinu/cloudsentry-multicloud-failover.git
cd cloudsentry-multicloud-failover

# Configure credentials
cp controller/config.py.example controller/config.py
# Fill in your Azure IP, AWS IP, and Cloudflare credentials

# Install dependencies
pip install flask flask-cors requests

# Start the controller and API
cd controller
python api_server.py

# Open the dashboard in Chrome
# dashboard/cloudsentry_dashboard.html
```

See [docs/setup-guide.md](docs/setup-guide.md) for full deployment instructions.

---

## Project Structure

```
cloudsentry-multicloud-failover/

  app/
    app.py                 Flask application
    requirements.txt       Python dependencies
    Dockerfile             App container definition
    docker-compose.yml     Multi-container setup
    nginx/
      nginx.conf           Reverse proxy configuration
      Dockerfile           Nginx container definition

  controller/
    config.py.example      Credentials template
    health_checker.py      HTTP health check logic
    cloudflare.py          Cloudflare DNS API wrapper
    controller.py          Standalone failover controller
    api_server.py          REST API for dashboard integration
    analyse_results.py     Trial results analysis script

  dashboard/
    cloudsentry_dashboard.html    Real-time monitoring UI

  results/
    all_results.csv        Raw data from 30 experimental trials

  docs/
    setup-guide.md         Full deployment instructions
    experiment-results.md  Results summary and analysis
```

---

## Experiment Results

The system was tested across six experimental conditions — three health check configurations combined with two failure types (VM failure and application failure), five repetitions each.

Full results: [docs/experiment-results.md](docs/experiment-results.md)

Raw trial data: [results/all_results.csv](results/all_results.csv)

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <sub>Built with Python · Docker · Azure · AWS · Cloudflare</sub>
</div>
