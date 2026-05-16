# Setup Guide

## Prerequisites

- Python 3.12+
- Docker Desktop
- AWS CLI configured with your credentials
- Azure CLI logged in to your subscription
- Cloudflare account with a domain

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/cloudsentry-multicloud-failover.git
cd cloudsentry-multicloud-failover
```

### 2. Configure credentials

```bash
cp controller/config.py.example controller/config.py
```

Open `controller/config.py` and fill in your values:
- Azure VM public IP
- AWS Elastic IP
- Cloudflare API token, Zone ID, and DNS record ID

### 3. Deploy the application to both cloud providers

**Azure:**
```bash
scp -r app/ azureuser@<AZURE_IP>:~/failover-app
ssh azureuser@<AZURE_IP> "cd ~/failover-app && PROVIDER=azure REGION=swedencentral docker compose up -d --build"
```

**AWS:**
```bash
scp -i failover-key.pem -r app/ ubuntu@<AWS_IP>:~/failover-app
ssh -i failover-key.pem ubuntu@<AWS_IP> "cd ~/failover-app && PROVIDER=aws REGION=eu-west-1 docker compose up -d --build"
```

### 4. Start the controller API

```bash
cd controller
pip install flask flask-cors requests
python api_server.py
```

### 5. Open the dashboard

Open `dashboard/cloudsentry_dashboard.html` in Chrome.

## Health Check Configurations

| Config | Interval | Timeout | Threshold | Theoretical RTO |
|--------|----------|---------|-----------|-----------------|
| A      | 5s       | 3s      | 2         | 10s             |
| B      | 15s      | 5s      | 3         | 45s             |
| C      | 30s      | 10s     | 5         | 150s            |
