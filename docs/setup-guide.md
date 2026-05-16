# Setup Guide

## Prerequisites
- Python 3.12+, Docker Desktop, AWS CLI, Azure CLI, Cloudflare account

## Quick Start
1. Clone the repo
2. `cp controller/config.py.example controller/config.py` and fill in your values
3. Deploy app to both cloud providers via SCP + Docker Compose
4. `pip install flask flask-cors requests`
5. `cd controller && python api_server.py`
6. Open `dashboard/cloudsentry_dashboard.html` in Chrome

## Health Check Configurations
| Config | Interval | Timeout | Threshold | Theoretical RTO |
|--------|----------|---------|-----------|-----------------|
| A      | 5s       | 3s      | 2         | 10s             |
| B      | 15s      | 5s      | 3         | 45s             |
| C      | 30s      | 10s     | 5         | 150s            |
